#!/usr/bin/env python3
"""Arm precisely one existing baseline MAC for the deployed bounded profiler.

Run on monitor-01 only under an explicitly approved Ansible play. Fail closed.
"""
import argparse
import json
import os
import re
import tempfile
import time
from pathlib import Path

INVENTORY = Path("/var/lib/homelab-network-hosts/inventory.json")
STATE = Path("/var/lib/homelab-network-hosts/deep-profiles.json")
PROFILER = Path("/usr/local/sbin/homelab-network-host-deep-profiler")
TARGET_IP = "192.168.2.186"
TARGET_MAC = "24:b2:b9:30:f8:55"


def check(now=None):
    now = int(time.time() if now is None else now)
    deployed = PROFILER.read_text()
    if not re.search(r'^SCAN_MODE\s*=\s*["\']targeted["\']\s*$', deployed, re.M):
        raise RuntimeError("Refusing: profiler is not targeted mode")
    if not re.search(r'^INTERFACE\s*=\s*["\']eth0["\']\s*$', deployed, re.M):
        raise RuntimeError("Refusing: unexpected profiler interface")
    if not re.search(r'^MAX_PROFILES_PER_RUN\s*=\s*\(\s*1\s*\)', deployed, re.M):
        raise RuntimeError("Refusing: max profiles per run not one")
    if not re.search(r'^ONE_ATTEMPT_PER_HOST\s*=\s*bool\(\s*1\s*\)', deployed, re.M):
        raise RuntimeError("Refusing: one-attempt policy not active")
    if not re.search(r'^BASELINE_BACKLOG_ENABLED\s*=\s*bool\(\s*0\s*\)', deployed, re.M):
        raise RuntimeError("Refusing: baseline backlog active")
    inventory = json.loads(INVENTORY.read_text())
    state = json.loads(STATE.read_text())
    if not isinstance(inventory, dict) or not isinstance(state, dict):
        raise RuntimeError("Refusing: invalid inventory or profile state")
    host = inventory.get(TARGET_IP)
    if not isinstance(host, dict) or str(host.get("mac", "")).lower() != TARGET_MAC:
        raise RuntimeError("Refusing: laptop IP/MAC not current")
    if host.get("online") is not True:
        raise RuntimeError("Refusing: laptop not online")
    if now - int(host.get("last_seen") or 0) not in range(0, 361):
        raise RuntimeError("Refusing: laptop discovery too old")
    profiles = state.get("profiles")
    if not isinstance(profiles, dict) or TARGET_MAC not in profiles:
        raise RuntimeError("Refusing: laptop baseline missing")
    if any(not isinstance(v, dict) or v.get("status") != "baseline" for v in profiles.values()):
        raise RuntimeError("Refusing: another profile is not baseline")
    record = profiles[TARGET_MAC]
    if (int(record.get("attempt_count") or 0) != 0
            or int(record.get("last_attempt") or 0) != 0
            or record.get("profile")):
        raise RuntimeError("Refusing: previous laptop scan evidence/attempt")
    if record.get("last_ip") != TARGET_IP:
        raise RuntimeError("Refusing: laptop profile IP mismatch")
    return state


def arm(state):
    state["profiles"][TARGET_MAC]["status"] = "pending"
    state["profiles"][TARGET_MAC]["discovered_at"] = int(time.time())
    fd, name = tempfile.mkstemp(prefix=".deep-profiles.arm.", dir=str(STATE.parent))
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(state, fh, indent=2, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(name, 0o600)
        os.replace(name, STATE)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", action="store_true")
    args = ap.parse_args()
    state = check()
    if args.arm:
        arm(state)
        print("ARMED_EXACTLY_ONE=192.168.2.186")
    else:
        print("PREFLIGHT_OK=192.168.2.186")


if __name__ == "__main__":
    main()
