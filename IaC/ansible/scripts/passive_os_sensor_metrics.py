#!/usr/bin/env python3
"""One-shot restricted SSH passive OS family candidates -> node-exporter textfile.

Only minimal, validated OS hints from an already sanitised router batch.
No MAC association, no authoritative OS override, no timers or service changes.
"""
import argparse
import hashlib
import ipaddress
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

LAN = ipaddress.ip_network("192.168.2.0/24")
FAMILIES = {"Linux", "Windows", "macOS", "Android", "iOS/iPadOS", "ChromeOS"}
KINDS = {"http", "dns", "tls", "quic"}
MAX_BYTES = 2 * 1024 * 1024 + 8192
MAX_EVENTS = 2000
KEY = "/etc/homelab/passive-os-ssh/id_ed25519"
KNOWN = "/etc/homelab/passive-os-ssh/known_hosts"
METRICS = Path("/var/lib/prometheus/node-exporter/homelab_passive_os_candidates.prom")
HEX64 = re.compile(r"^[a-f0-9]{64}$")


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate wire field")
        result[key] = value
    return result


def validate(raw):
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_BYTES:
        raise ValueError("Invalid wire size")
    batch = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique)
    if not isinstance(batch, dict) or set(batch) != {
        "protocol", "batch_id", "digest", "observations"
    } or type(batch["protocol"]) is not int or batch["protocol"] != 1:
        raise ValueError("Invalid wire structure")
    if not all(isinstance(batch[k], str) and HEX64.fullmatch(batch[k])
               for k in ("batch_id", "digest")):
        raise ValueError("Invalid wire identity")
    observations = batch["observations"]
    if not isinstance(observations, list) or len(observations) > MAX_EVENTS:
        raise ValueError("Invalid observations")
    for event in observations:
        if not isinstance(event, dict) or not (
            {"src_ip", "timestamp", "event_type"} <= set(event) <=
            {"src_ip", "timestamp", "event_type", "os_family_hint"}
        ):
            raise ValueError("Invalid event fields")
        ip = event["src_ip"]
        if not isinstance(ip, str):
            raise ValueError("Invalid event IP")
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            raise ValueError("Invalid event IP") from None
        if addr not in LAN or str(addr) != ip or addr in (
            LAN.network_address, LAN.broadcast_address, LAN.network_address + 1
        ):
            raise ValueError("Invalid LAN client")
        if type(event["timestamp"]) is not int or not 1577836800 <= event["timestamp"] <= 4102444800:
            raise ValueError("Invalid event timestamp")
        kind = event["event_type"]
        if kind not in KINDS:
            raise ValueError("Invalid event type")
        if "os_family_hint" in event and (
            kind != "http" or event["os_family_hint"] not in FAMILIES
        ):
            raise ValueError("Invalid OS family hint")
    canonical = json.dumps(observations, sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(canonical).hexdigest() != batch["digest"]:
        raise ValueError("Wire digest mismatch")
    return batch


def metrics_for(batch):
    counts = {}
    last_seen = {}
    for event in batch["observations"]:
        family = event.get("os_family_hint")
        if not family:
            continue
        key = (event["src_ip"], family)
        counts[key] = counts.get(key, 0) + 1
        last_seen[key] = max(last_seen.get(key, 0), event["timestamp"])
    lines = [
        "# HELP homelab_passive_os_candidate_info Unverified self-reported OS family candidate (not authoritative).",
        "# TYPE homelab_passive_os_candidate_info gauge",
        "# HELP homelab_passive_os_candidate_observations HTTP observations supporting the passive candidate.",
        "# TYPE homelab_passive_os_candidate_observations gauge",
        "# HELP homelab_passive_os_candidate_last_seen_seconds Latest supporting observation timestamp.",
        "# TYPE homelab_passive_os_candidate_last_seen_seconds gauge",
    ]
    for (ip, family), count in sorted(counts.items()):
        labels = (f'ip="{ip}",os_family="{family}",source="http_user_agent",'
                  'confidence="low",mac_attribution="unverified"')
        lines.extend([
            f"homelab_passive_os_candidate_info{{{labels}}} 1",
            f"homelab_passive_os_candidate_observations{{{labels}}} {count}",
            f"homelab_passive_os_candidate_last_seen_seconds{{{labels}}} {last_seen[(ip, family)]}",
        ])
    return ("\n".join(lines) + "\n").encode(), len(counts)


def publish(target, payload):
    if os.geteuid() != 0:
        raise PermissionError("Root required")
    info = target.parent.stat()
    if not target.parent.is_dir() or info.st_uid != 0:
        raise ValueError("Unexpected metric directory owner")
    if target.is_symlink():
        raise ValueError("Metric path symlink refused")
    if target.exists() and (not target.is_file() or target.stat().st_uid != 0):
        raise ValueError("Untrusted existing metric path")
    fd, temp = tempfile.mkstemp(dir=target.parent, prefix=".passive-os-")
    try:
        os.fchmod(fd, 0o644)
        with os.fdopen(fd, "wb") as out:
            out.write(payload)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temp, target)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=METRICS)
    args = ap.parse_args()
    proc = subprocess.run([
        "/usr/bin/ssh", "-T", "-i", KEY, "-o", "IdentitiesOnly=yes",
        "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
        "-o", "UserKnownHostsFile=" + KNOWN, "-o", "ConnectTimeout=5",
        "homelab-os-transfer@192.168.2.1", "get-batch",
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
       timeout=20, check=False)
    if proc.returncode != 0:
        raise RuntimeError("Restricted router SSH fetch failed")
    batch = validate(proc.stdout)
    payload, candidates = metrics_for(batch)
    publish(args.output, payload)
    print(json.dumps({
        "status": "published", "batch_id": batch["batch_id"],
        "observations": len(batch["observations"]),
        "distinct_ip_family_candidates": candidates,
        "metric_bytes": len(payload),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
