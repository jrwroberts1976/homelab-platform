#!/usr/bin/env python3
"""Pure, side-effect-free PPP QoS reconciliation planner (not a deployable actuator).

The planner never invokes ip/tc/systemctl. Snapshot and ownership data are
provided as JSON, enabling deterministic test cases before any live integration.
"""
import json
import sys


def plan(snapshot):
    event = snapshot["event"]
    if event not in ("up", "down"):
        raise ValueError("event must be up or down")
    iface = snapshot["interface"]
    if iface != "ppp0":
        return {"decision": "ignore", "reason": "unmanaged interface", "actions": []}
    previous = snapshot.get("owned")
    current = snapshot.get("ifindex")
    qdisc = snapshot.get("qdisc", "none")
    filters = snapshot.get("filters", [])
    if not isinstance(filters, list):
        raise ValueError("filters must be a list")
    if event == "down":
        if not previous:
            return {"decision": "noop", "reason": "nothing owned", "actions": []}
        if current is None or current != previous["ifindex"]:
            return {"decision": "cleanup_stale", "reason": "old PPP interface absent or replaced",
                    "actions": ["remove_owned_ifb", "clear_owned_state"]}
        if qdisc != "owned_clsact" or any(item != "owned_redirect" for item in filters):
            return {"decision": "refuse", "reason": "unexpected ingress ownership", "actions": []}
        return {"decision": "detach", "reason": "matching owned PPP interface",
                "actions": ["remove_owned_redirect", "remove_owned_clsact",
                            "remove_owned_ifb", "clear_owned_state"]}
    if current is None:
        return {"decision": "defer", "reason": "PPP interface not present", "actions": []}
    if not snapshot.get("default_route_on_ppp", False) or not snapshot.get("upload_cake_ok", False):
        return {"decision": "defer", "reason": "WAN prerequisites not ready", "actions": []}
    if previous:
        if previous["ifindex"] == current:
            if qdisc == "owned_clsact" and filters == ["owned_redirect"]:
                return {"decision": "noop", "reason": "already configured", "actions": []}
            return {"decision": "refuse", "reason": "owned state inconsistent", "actions": []}
        if qdisc != "none" or filters:
            return {"decision": "refuse", "reason": "replacement PPP has foreign ingress", "actions": []}
        return {"decision": "reconnect", "reason": "PPP identity changed",
                "actions": ["remove_owned_ifb", "clear_owned_state",
                            "arm_independent_rollback", "create_owned_ifb",
                            "apply_43mbit_cake", "attach_owned_redirect", "verify"]}
    if qdisc != "none" or filters or snapshot.get("ifb_exists", False):
        return {"decision": "refuse", "reason": "resources already exist and are not owned", "actions": []}
    return {"decision": "attach", "reason": "clean PPP ingress",
            "actions": ["arm_independent_rollback", "create_owned_ifb",
                        "apply_43mbit_cake", "attach_owned_redirect", "verify"]}


def main():
    snapshot = json.load(sys.stdin)
    print(json.dumps(plan(snapshot), sort_keys=True))


if __name__ == "__main__":
    main()
