#!/usr/bin/env python3
"""Isolated synthetic Pi-hole -> Alloy -> local Loki receiver privacy test."""
import http.server
import json
import pathlib
import re
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.request
import snappy

CANDIDATE = pathlib.Path("/tmp/pihole-alloy-candidate.alloy")
PYTHON_LOG = "privacy-test.log"
SENTINELS = ("private-test.example", "198.51.100.77", "secret-should-drop.example")
EXPECTED = {"query[A]", "gravity blocked", "forwarded", "reply"}
RECEIVED = []

def varint(data, offset):
    value, shift = 0, 0
    while True:
        byte = data[offset]
        offset += 1
        value |= (byte & 127) << shift
        if byte < 128:
            return value, offset
        shift += 7

def fields(data):
    offset = 0
    while offset < len(data):
        key, offset = varint(data, offset)
        number, wire = key >> 3, key & 7
        if wire == 0:
            value, offset = varint(data, offset)
        elif wire == 1:
            value, offset = data[offset:offset + 8], offset + 8
        elif wire == 2:
            length, offset = varint(data, offset)
            value, offset = data[offset:offset + length], offset + length
        elif wire == 5:
            value, offset = data[offset:offset + 4], offset + 4
        else:
            raise ValueError("Unsupported protobuf wire type")
        yield number, wire, value

def decode_push(data):
    # Loki PushRequest: streams field 1; Stream: entries field 2;
    # Entry: line field 2.
    result = []
    for number, wire, stream in fields(snappy.decompress(data)):
        if number != 1 or wire != 2:
            continue
        for n, w, entry in fields(stream):
            if n != 2 or w != 2:
                continue
            for en, ew, line in fields(entry):
                if en == 2 and ew == 2:
                    result.append(line.decode("utf-8"))
    return result

class Receiver(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        try:
            RECEIVED.extend(decode_push(body))
            self.send_response(204)
        except Exception as exc:
            RECEIVED.append("DECODE_ERROR:" + str(exc))
            self.send_response(400)
        self.end_headers()

    def log_message(self, *_):
        pass

def main():
    original = CANDIDATE.read_text()
    start = original.index('local.file_match "pihole" {')
    end = original.index('\nloki.write "homelab" {', start)
    pipeline = original[start:end]
    # Retain the actual rendered production Pi-hole processing stages.
    with tempfile.TemporaryDirectory(prefix="alloy-pihole-test-") as tmp:
        directory = pathlib.Path(tmp)
        log = directory / PYTHON_LOG
        log.write_text("")
        pipeline = pipeline.replace('/var/log/pihole/pihole.log', str(log))
        config = directory / "test.alloy"
        config.write_text(pipeline + '\nloki.write "homelab" {\n endpoint { url = "http://127.0.0.1:13101/loki/api/v1/push" }\n}\n')
        subprocess.run(["/usr/bin/alloy", "validate", str(config)], check=True)
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 13101), Receiver)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        proc = subprocess.Popen(
            ["/usr/bin/alloy", "run", "--server.http.listen-addr=127.0.0.1:12347", str(config)],
            stdout=(directory / "alloy.stdout").open("w"),
            stderr=subprocess.STDOUT,
        )
        try:
            for _ in range(50):
                if proc.poll() is not None:
                    raise RuntimeError("Temporary Alloy exited: " + (directory / "alloy.stdout").read_text()[-3000:])
                try:
                    urllib.request.urlopen("http://127.0.0.1:12347/-/ready", timeout=0.2)
                    break
                except Exception:
                    time.sleep(0.2)
            time.sleep(2)
            lines = [
                "Sep 23 08:00:01 dns-01 pihole-FTL[123]: query[A] private-test.example from 198.51.100.77",
                "Sep 23 08:00:02 dns-01 pihole-FTL[123]: gravity blocked private-test.example is 0.0.0.0",
                "Sep 23 08:00:03 dns-01 pihole-FTL[123]: forwarded private-test.example to 1.1.1.1",
                "Sep 23 08:00:04 dns-01 pihole-FTL[123]: reply private-test.example is 192.0.2.1",
                "Sep 23 08:00:05 dns-01 pihole-FTL[123]: malformed secret-should-drop.example from 198.51.100.77",
                "Sep 23 08:00:06 dns-01 pihole-FTL[123]: query[A] secret-should-drop.example from ",
            ]
            with log.open("a") as handle:
                handle.write("\n".join(lines) + "\n")
                handle.flush()
            for _ in range(60):
                if EXPECTED.issubset(set(RECEIVED)):
                    break
                time.sleep(0.5)
            actual = set(RECEIVED)
            forbidden = [s for s in SENTINELS if any(s in entry for entry in RECEIVED)]
            unexpected = actual - {"query[A]", "gravity blocked", "forwarded", "reply"}
            print("Received event tokens:", json.dumps(sorted(actual)))
            print("Required event tokens present:", EXPECTED.issubset(actual))
            print("Sensitive sentinels received:", forbidden)
            print("Unexpected outgoing messages:", sorted(unexpected))
            if not EXPECTED.issubset(actual) or forbidden or unexpected:
                raise SystemExit("PRIVACY_TEST=FAIL")
            print("PRIVACY_TEST=PASS")
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            server.shutdown()

if __name__ == "__main__":
    main()
