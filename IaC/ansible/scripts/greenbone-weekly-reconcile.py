#!/usr/bin/env python3
"""Greenbone weekly schedule reconciler. Dry-run by default; --apply changes GMP."""
import argparse
import json
import socket
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

TARGET_FULL = "23d32a1e-ce0c-4d89-9bc5-76da688b2909"
TARGET_AUTH = "1c8418b5-1cae-4cca-8535-4700c2d2835b"
AUTH_TASK = "02b610fc-647a-4fb8-98c3-7763e0425c34"
CONFIG = "daba56c8-73ec-11df-a475-002264764cea"
SCANNER = "08b69003-5fc2-4037-a479-93b440211c73"
FULL_NAME = "Homelab - Full LAN - Weekly"
FULL_SCHEDULE = "Homelab - Full LAN - Weekly Schedule"
AUTH_SCHEDULE = "Homelab - Authenticated - Weekly Schedule"

def xml_text(value):
    return escape(value, {'"': '&quot;'})

def text(element, child):
    found = element.find(child)
    return (found.text or "").strip() if found is not None else ""

def query(sock, xml):
    sock.sendall(xml.encode())
    parser = ET.XMLPullParser(events=("start", "end"))
    level = 0
    top = None
    while True:
        chunk = sock.recv(65536)
        if not chunk:
            raise RuntimeError("GMP disconnected")
        parser.feed(chunk.decode())
        for event, element in parser.read_events():
            if event == "start":
                level += 1
                if top is None:
                    top = element
            else:
                level -= 1
                if level == 0:
                    code = int(top.get("status", "500"))
                    if not 200 <= code < 300:
                        raise RuntimeError("GMP returned status " + str(code) + " for " + top.tag)
                    return top

def exact_one(parent, tag, *, name=None, uuid=None):
    matches = [e for e in parent.findall(tag) if (name is None or text(e, "name") == name) and (uuid is None or e.get("id") == uuid)]
    if len(matches) != 1:
        raise RuntimeError("Expected exactly one matching " + tag + ": " + str(len(matches)))
    return matches[0]

def calendar(day, hour):
    # First date in the future for the specified weekday; same-day recurrence follows RRULE.
    # Anchor 2026-10-25 is a Sunday; use 2026-10-28 for Wednesday.
    anchor = "20261025" if day == "SU" else "20261028"
    return ("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//homelab-platform//Greenbone Weekly//EN\n"
            "BEGIN:VEVENT\nDTSTART;TZID=Europe/London:" + anchor + "T" + hour + "0000\n"
            "RRULE:FREQ=WEEKLY;BYDAY=" + day + "\nEND:VEVENT\nEND:VCALENDAR\n")

def create_schedule(sock, name, ical):
    command = "<create_schedule><name>" + xml_text(name) + "</name><timezone>Europe/London</timezone><icalendar>" + xml_text(ical) + "</icalendar></create_schedule>"
    response = query(sock, command)
    return response.get("id", "")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    username = sys.stdin.readline().rstrip("\n")
    password = sys.stdin.readline().rstrip("\n")
    if not username or not password:
        raise RuntimeError("GMP credentials required on stdin")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(90)
        sock.connect("/run/gvmd/gvmd.sock")
        query(sock, "<authenticate><credentials><username>" + xml_text(username) + "</username><password>" + xml_text(password) + "</password></credentials></authenticate>")
        password = None
        targets = query(sock, '<get_targets filter="rows=-1"/>')
        tasks = query(sock, '<get_tasks details="1" filter="rows=-1"/>')
        schedules = query(sock, '<get_schedules filter="rows=-1"/>')
        full_target = exact_one(targets, "target", uuid=TARGET_FULL)
        auth_target = exact_one(targets, "target", uuid=TARGET_AUTH)
        auth_task = exact_one(tasks, "task", uuid=AUTH_TASK)
        auth_ref = auth_task.find("target")
        if auth_ref is None or auth_ref.get("id") != TARGET_AUTH:
            raise RuntimeError("Authenticated task target changed")
        ssh = auth_target.find("ssh_credential")
        if ssh is None or not ssh.get("id"):
            raise RuntimeError("Authenticated target has no SSH credential")
        for target in (full_target, auth_target):
            if not text(target, "hosts"):
                raise RuntimeError("Target empty: " + text(target, "name"))
        all_full = [e for e in tasks.findall("task") if text(e, "name") == FULL_NAME]
        if len(all_full) > 1:
            raise RuntimeError("Duplicate weekly full scan names")
        if all_full:
            t = all_full[0]
            for field, expected in (("target", TARGET_FULL), ("config", CONFIG), ("scanner", SCANNER)):
                node = t.find(field)
                if node is None or node.get("id") != expected:
                    raise RuntimeError("Existing full weekly scan has incompatible " + field)
        if text(auth_task, "status").lower() in ("running", "requested", "queued") and args.apply:
            raise RuntimeError("Authenticated task is currently in progress; refusing to modify schedules")
        for name in (FULL_SCHEDULE, AUTH_SCHEDULE):
            if len([s for s in schedules.findall("schedule") if text(s, "name") == name]) > 1:
                raise RuntimeError("Duplicate named schedules: " + name)
        summary = {"mode": "APPLY" if args.apply else "DRY_RUN", "full_task_existing": bool(all_full),
                   "authenticated_task_status": text(auth_task, "status"), "authenticated_task_id": AUTH_TASK,
                   "full_target": text(full_target, "name"), "authenticated_target": text(auth_target, "name"),
                   "ssh_auth_configured": True, "weekly_full": "Sunday 03:00 Europe/London",
                   "weekly_authenticated": "Wednesday 03:00 Europe/London"}
        if not args.apply:
            print(json.dumps(summary, indent=2))
            return
        weekly = {}
        for name, day in ((FULL_SCHEDULE, "SU"), (AUTH_SCHEDULE, "WE")):
            matches = [s for s in schedules.findall("schedule") if text(s, "name") == name]
            intended = calendar(day, "03")
            if matches:
                schedule = matches[0]
                if text(schedule, "timezone") != "Europe/London" or text(schedule, "icalendar").strip() != intended.strip():
                    raise RuntimeError("Existing schedule drift: " + name)
                weekly[name] = schedule.get("id")
            else:
                weekly[name] = create_schedule(sock, name, intended)
        if not all_full:
            response = query(sock, '<create_task><name>' + xml_text(FULL_NAME) + '</name><comment>Weekly LAN scan managed by homelab-platform Ansible</comment><config id="' + CONFIG + '"/><target id="' + TARGET_FULL + '"/><scanner id="' + SCANNER + '"/><schedule id="' + weekly[FULL_SCHEDULE] + '"/></create_task>')
            summary["full_task_id"] = response.get("id")
        else:
            full = all_full[0]
            summary["full_task_id"] = full.get("id")
            if full.find("schedule") is None or full.find("schedule").get("id") != weekly[FULL_SCHEDULE]:
                query(sock, '<modify_task task_id="' + full.get("id") + '"><schedule id="' + weekly[FULL_SCHEDULE] + '"/></modify_task>')
        attached = auth_task.find("schedule")
        if attached is None or attached.get("id") != weekly[AUTH_SCHEDULE]:
            query(sock, '<modify_task task_id="' + AUTH_TASK + '"><schedule id="' + weekly[AUTH_SCHEDULE] + '"/></modify_task>')
        summary["result"] = "Weekly schedules reconciled; no scans started or stopped"
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, ET.ParseError) as exc:
        print("WEEKLY_RECONCILE_ERROR=" + type(exc).__name__ + ": " + str(exc), file=sys.stderr)
        sys.exit(2)
