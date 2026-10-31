#!/usr/bin/env python3
"""Offline actuator simulator; never executes ip, tc, systemctl or PPP hooks.

Tests apply/reconcile/rollback ordering and crash recovery using JSON state
only. Not suitable for deployment on router-01.
"""
import argparse
import fcntl
import json
from pathlib import Path


def apply_event(state, event, fail_at=None):
    state = dict(state)
    actions = []
    if event == "down":
        if state.get("attached"):
            actions.extend(["remove_redirect", "remove_clsact"])
        if state.get("ifb"):
            actions.append("remove_ifb")
        state.update(attached=False, ifb=False, ifindex=None, rollback_armed=False)
        return state, actions
    if event != "up":
        raise ValueError("invalid event")
    if state.get("attached"):
        return state, ["noop"]
    for action, key, value in [
        ("arm_rollback", "rollback_armed", True),
        ("create_ifb", "ifb", True),
        ("attach_ingress", "attached", True),
    ]:
        actions.append(action)
        state[key] = value
        if action == fail_at:
            actions.append("simulated_crash")
            return state, actions
    return state, actions


def recover(state):
    actions = []
    state = dict(state)
    if state.get("rollback_armed"):
        if state.get("attached"):
            actions.append("remove_redirect_and_clsact")
        if state.get("ifb"):
            actions.append("remove_ifb")
        state.update(attached=False, ifb=False, rollback_armed=False)
    return state, actions


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lock", required=True)
    ap.add_argument("--event", choices=["up", "down"], required=True)
    ap.add_argument("--fail-at", choices=["arm_rollback", "create_ifb", "attach_ingress"])
    ap.add_argument("--state", required=True)
    args = ap.parse_args()
    path = Path(args.state)
    with open(args.lock, "a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = json.loads(path.read_text()) if path.exists() else {}
        state, actions = apply_event(state, args.event, args.fail_at)
        if args.fail_at is not None:
            state, recovery = recover(state)
            actions += recovery
        path.write_text(json.dumps(state, sort_keys=True))
    print(json.dumps({"actions": actions, "state": state}, sort_keys=True))


if __name__ == "__main__":
    main()
