#!/usr/bin/env python3
"""Safely refresh Greenbone Community feed images, not application containers.

Run only as root via the systemd unit. Explicit --apply required.
Greenbone daemon import is asynchronous; this script never claims import complete.
"""
import argparse
import datetime
import fcntl
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path("/opt/greenbone-community")
RUNNER = Path("/usr/local/sbin/homelab-greenbone-scan")
LOCK = Path("/run/lock/homelab-greenbone-scan.lock")
STATUS = Path("/var/lib/homelab-greenbone-scanning/feed-refresh.json")
FEEDS = ("notus-data", "vulnerability-tests", "scap-data",
         "dfn-cert-data", "cert-bund-data", "report-formats", "data-objects")
ACTIVE = {"Running", "Requested", "Queued", "Stop Requested", "Processing"}
COMPOSE = ["docker", "compose", "-f", str(ROOT / "compose.yaml"),
           "-f", str(ROOT / "compose.override.yaml")]

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def state(status, **extra):
    STATUS.parent.mkdir(parents=True, exist_ok=True, mode=0o750)
    payload = {"checked_at": now(), "state": status, **extra}
    tmp = STATUS.with_suffix(".json.tmp")
    with tmp.open("w") as f:
        json.dump(payload, f, sort_keys=True, indent=2)
        f.write("\n")
    os.chmod(tmp, 0o640)
    os.replace(tmp, STATUS)
    print("FEED_REFRESH=" + status, flush=True)

def task_states(gmp):
    xml = gmp('<get_tasks details="0" filter="rows=-1"/>', timeout_seconds=90)
    return [(task.findtext("name", ""), task.findtext("status", ""))
            for task in xml.findall(".//task")
            if task.findtext("status", "") in ACTIVE]

def check(gmp):
    tasks = task_states(gmp)
    if tasks:
        print("ACTIVE_TASK_COUNT=" + str(len(tasks)), flush=True)
        for name, status in tasks:
            print("ACTIVE_TASK=" + name + " STATUS=" + status, flush=True)
        return False
    print("ACTIVE_TASK_COUNT=0", flush=True)
    return True

def command(argv, timeout):
    subprocess.run(argv, check=True, timeout=timeout)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if os.geteuid() != 0:
        raise RuntimeError("Root privileges required")
    for path in (ROOT / "compose.yaml", ROOT / "compose.override.yaml", RUNNER):
        if not path.is_file():
            raise RuntimeError("Required existing deployment file missing: " + str(path))
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with LOCK.open("a+") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            state("SKIPPED_RUNNER_ACTIVE")
            return
        # Load existing protected GMP client. Never print credentials.
        gmp = runpy.run_path(str(RUNNER), run_name="greenbone_feed_refresh")["gmp"]
        if not check(gmp):
            state("SKIPPED_ACTIVE_SCAN")
            return
        command(COMPOSE + ["config", "--quiet"], 60)
        if not args.apply:
            print("FEED_REFRESH=DRY_RUN no downloads or container changes", flush=True)
            return
        state("PULLING")
        # Only the seven upstream feed images; no database/scanner/web images.
        command(COMPOSE + ["pull", *FEEDS], 7200)
        # Recheck GMP before modifying data volumes. Lock also blocks our
        # Ansible-managed scan runner from starting during the operation.
        if not check(gmp):
            state("SKIPPED_AFTER_PULL_ACTIVE_SCAN")
            return
        state("APPLYING")
        # Dependencies are already running. --no-deps prevents compose from
        # reconciling gvmd, PostgreSQL, scanner or web containers.
        command(COMPOSE + ["up", "-d", "--no-deps", *FEEDS], 3600)
        state("FEED_CONTAINERS_UPDATED_IMPORT_PENDING",
              note="Greenbone imports feed content asynchronously; verify feed status in GSA")
    return

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        try:
            state("FAILED", error=type(exc).__name__ + ": " + str(exc))
        except Exception:
            pass
        print("ERROR: " + str(exc), file=sys.stderr)
        sys.exit(1)
