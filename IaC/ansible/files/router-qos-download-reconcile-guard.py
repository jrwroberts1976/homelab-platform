#!/usr/bin/env python3
"""Controller-testable reconciliation guard. Does not invoke networking commands.

Serialize events through flock, validate an owned-state snapshot, and delegate
all decisions to the existing pure planner. No production executor is wired in.
"""
import argparse
import fcntl
import json
from pathlib import Path
import sys

import importlib.util

PLANNER = Path(__file__).with_name('router-qos-download-reconcile-plan.py')
spec = importlib.util.spec_from_file_location('qos_plan', PLANNER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
plan = module.plan


def guarded_plan(snapshot_path, lock_path):
    with open(lock_path, "a+", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        snapshot = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
        if snapshot.get("owned") is not None:
            owned = snapshot["owned"]
            if not isinstance(owned, dict) or type(owned.get("ifindex")) is not int or owned["ifindex"] <= 0:
                return {"decision": "refuse", "reason": "invalid owned identity", "actions": []}
        if snapshot.get("ifindex") is not None and (type(snapshot["ifindex"]) is not int or snapshot["ifindex"] <= 0):
            return {"decision": "refuse", "reason": "invalid current identity", "actions": []}
        return plan(snapshot)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--lock", required=True)
    args = parser.parse_args()
    print(json.dumps(guarded_plan(args.snapshot, args.lock), sort_keys=True))


if __name__ == "__main__":
    main()
