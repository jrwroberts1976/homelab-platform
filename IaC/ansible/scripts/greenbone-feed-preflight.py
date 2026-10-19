#!/usr/bin/env python3
"""Greenbone feed refresh preflight. Read-only; never pulls or restarts containers."""
import runpy
import sys

ACTIVE = {"Running", "Requested", "Queued", "Stop Requested", "Processing"}
try:
    runner = runpy.run_path("/usr/local/sbin/homelab-greenbone-scan", run_name="greenbone_feed_preflight")
    root = runner["gmp"]('<get_tasks details="0" filter="rows=-1"/>')
    active = [(t.findtext("name", ""), t.findtext("status", "")) for t in root.findall(".//task")
              if t.findtext("status", "") in ACTIVE]
    print("ACTIVE_TASK_COUNT=" + str(len(active)))
    for name, status in active:
        print("ACTIVE_TASK=" + name + " STATUS=" + status)
    if active:
        print("FEED_REFRESH_SAFE=NO active Greenbone scans")
        sys.exit(2)
    print("FEED_REFRESH_SAFE=YES (GMP preflight only; no changes performed)")
except Exception as exc:
    print("FEED_REFRESH_SAFE=UNKNOWN " + str(exc), file=sys.stderr)
    sys.exit(1)
