#!/usr/bin/env python3
"""Read-only Phase 5 watchdog probe. Sensor-01 test namespace only.

This probe does NOT arm a watchdog, certify rollback, or mutate networking.
A successful snapshot is only diagnostic evidence, not authorization to install.
"""
import argparse
import json
from pathlib import Path
import subprocess
import time

NS = "qos-p5"
UNIT = "qos-p5-rollback.timer"
CALLBACK = Path("/run/qos-p5-rollback.sh")
OWNER = Path("/run/qos-p5/ns-inode")

def command(*argv):
    return subprocess.run(argv, capture_output=True, text=True, check=False, timeout=3)

def probe():
    name = command("hostname", "-s")
    if name.returncode != 0 or name.stdout.strip() != "sensor-01":
        raise RuntimeError("refusing non-sensor host")
    host = command("stat", "-Lc", "%i", "/proc/1/ns/net")
    ns = command("stat", "-Lc", "%i", f"/run/netns/{NS}")
    timer = command("systemctl", "is-active", UNIT)
    deadline = command("systemctl", "show", UNIT, "-p", "NextElapseUSecMonotonic", "--value")
    inode = int(ns.stdout.strip()) if ns.returncode == 0 and ns.stdout.strip().isdigit() else None
    host_inode = int(host.stdout.strip()) if host.returncode == 0 and host.stdout.strip().isdigit() else None
    owner_inode = int(OWNER.read_text().strip()) if OWNER.is_file() and OWNER.read_text().strip().isdigit() else None
    now_us = time.clock_gettime_ns(time.CLOCK_MONOTONIC) // 1000
    # systemd's monotonic deadline property is a duration-format timestamp on
    # some versions, NOT necessarily an integer; refuse unparseable values.
    raw_deadline = deadline.stdout.strip()
    deadline_us = int(raw_deadline) if deadline.returncode == 0 and raw_deadline.isdecimal() else None
    return {
        "namespace": NS,
        "namespace_inode": inode,
        "host_inode": host_inode,
        "owned_inode": owner_inode,
        "timer_unit": UNIT,
        "timer_active": timer.returncode == 0 and timer.stdout.strip() == "active",
        "callback_path": str(CALLBACK),
        "callback_exists": CALLBACK.is_file() and not CALLBACK.is_symlink(),
        "deadline_monotonic_us": deadline_us,
        "now_monotonic_us": now_us,
        "verified_for_mutation": False,
        "network_modified": False,
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(probe(), sort_keys=True))
