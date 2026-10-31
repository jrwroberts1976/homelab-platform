#!/usr/bin/env python3
"""Offline Phase 5 PPP event transition runner. NEVER invokes ip/tc/systemd."""
import argparse
import json
from dataclasses import dataclass

@dataclass(frozen=True)
class Session:
    generation: str
    ifindex: int

def step(owned, event):
    kind = event["event"]
    current = Session(event["generation"], event["ifindex"])
    if kind not in ("up", "down") or current.ifindex <= 0:
        raise ValueError("invalid event")
    if event.get("foreign", False) or event.get("partial", False):
        return owned, "REFUSE_UNVERIFIED", []
    if kind == "up":
        if owned == current:
            return owned, "NOOP", []
        if owned is not None:
            return owned, "REFUSE_OLD_SESSION_PRESENT", []
        return current, "PLAN_INSTALL", ["arm_rollback", "verify_ppp_identity", "attach_owned_ifb"]
    if owned is None:
        return None, "NOOP", []
    if owned != current:
        return owned, "REFUSE_STALE_DOWN", []
    return None, "PLAN_TEARDOWN", ["verify_owned_state", "detach_owned_redirect", "remove_owned_ifb"]

def replay(events):
    owned = None
    result = []
    for ev in events:
        proposal, decision, operations = step(owned, ev)
        # Mutation below is in-memory only; caller supplies fake event stream.
        if ev.get("fail_before_commit"):
            result.append({"decision": "INJECTED_FAILURE", "proposed": decision, "operations": operations})
            continue
        owned = proposal
        result.append({"decision": decision, "operations": operations})
    return {"transitions": result, "owned": None if owned is None else vars(owned), "network_modified": False}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fixture")
    args = ap.parse_args()
    with open(args.fixture, encoding="utf-8") as f:
        events = json.load(f)
    if not isinstance(events, list):
        raise ValueError("expected array of PPP events")
    print(json.dumps(replay(events), sort_keys=True))

if __name__ == "__main__":
    main()
