#!/usr/bin/env python3
"""Read-only GMP inventory. Credentials via stdin; outputs only task metadata."""
import json
import socket
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

def query(sock, xml):
    sock.sendall(xml.encode())
    parser = ET.XMLPullParser(events=("start", "end"))
    depth = 0
    root = None
    while True:
        block = sock.recv(65536)
        if not block:
            raise RuntimeError("GMP connection closed")
        parser.feed(block.decode())
        for event, element in parser.read_events():
            if event == "start":
                depth += 1
                if root is None:
                    root = element
            else:
                depth -= 1
                if depth == 0:
                    code = int(root.get("status", "500"))
                    if not 200 <= code < 300:
                        raise RuntimeError("GMP status " + str(code))
                    return root

def value(e, tag):
    child = e.find(tag)
    return (child.text or "").strip() if child is not None else ""

def ref(e, tag):
    child = e.find(tag)
    return {"id": child.get("id", ""), "name": value(child, "name")} if child is not None else {"id": "", "name": ""}

def main():
    username = sys.stdin.readline().rstrip("\n")
    password = sys.stdin.readline().rstrip("\n")
    if not username or not password:
        raise RuntimeError("GMP credentials missing")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(60)
        sock.connect("/run/gvmd/gvmd.sock")
        query(sock, "<authenticate><credentials><username>" + escape(username) + "</username><password>" + escape(password) + "</password></credentials></authenticate>")
        password = None
        tasks = query(sock, '<get_tasks details="1" filter="rows=-1"/>')
        targets = query(sock, '<get_targets filter="rows=-1"/>')
        schedules = query(sock, '<get_schedules filter="rows=-1"/>')
    result = {"tasks": [], "targets": [], "schedules": []}
    for t in tasks.findall("task"):
        result["tasks"].append({"id": t.get("id", ""), "name": value(t, "name"), "status": value(t, "status"), "target": ref(t, "target"), "config": ref(t, "config"), "scanner": ref(t, "scanner"), "schedule": ref(t, "schedule")})
    for t in targets.findall("target"):
        ssh = ref(t, "ssh_credential")
        result["targets"].append({"id": t.get("id", ""), "name": value(t, "name"), "hosts": value(t, "hosts"), "ssh_auth_configured": bool(ssh["id"]), "ssh_credential_name": ssh["name"] if ssh["id"] else ""})
    for s in schedules.findall("schedule"):
        result["schedules"].append({"id": s.get("id", ""), "name": value(s, "name"), "timezone": value(s, "timezone"), "icalendar": value(s, "icalendar")})
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, ET.ParseError) as exc:
        print("GMP_INVENTORY_ERROR=" + type(exc).__name__ + ": " + str(exc), file=sys.stderr)
        sys.exit(2)
