#!/usr/bin/env python3
"""Phase 5 PPP lifecycle reconciler: READ-ONLY planner, never changes the network.

Not a production hook. Actions are proposals only until separate approved,
ownership-verified mutator and watchdog are implemented and tested.
"""
import argparse
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Session:
    interface: str
    ifindex: int
    token: str

    @classmethod
    def from_mapping(cls, data):
        if not isinstance(data, dict):
            raise ValueError("session must be a mapping")
        name, index, token = data["interface"], data["ifindex"], data["token"]
        if name != "ppp0" or type(index) is not int or index <= 0:
            raise ValueError("invalid PPP interface or ifindex")
        if not isinstance(token, str) or not (1 <= len(token) <= 128):
            raise ValueError("missing or invalid session token")
        return cls(name, index, token)


def decide(event, incoming, owned=None, foreign=False, partial=False):
    """Return a no-side-effect decision, rejecting ambiguous ownership."""
    if event not in ("up", "down"):
        raise ValueError("event must be up or down")
    if foreign or partial:
        return "REFUSE_UNVERIFIED_RESOURCES"
    if event == "up":
        if owned is None:
            return "ARM_WATCHDOG_BEFORE_INSTALL"
        if owned == incoming:
            return "NOOP_ALREADY_CURRENT"
        return "REQUIRE_VERIFIED_OLD_SESSION_TEARDOWN"
    if owned is None:
        return "NOOP_NOT_OWNED"
    if owned != incoming:
        return "REFUSE_STALE_DOWN_EVENT"
    return "VERIFY_OWNERSHIP_THEN_REMOVE"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", choices=("up", "down"), required=True)
    parser.add_argument("--input", required=True, help="JSON fixture containing incoming and optional owned session")
    args = parser.parse_args()
    with open(args.input, encoding="utf-8") as stream:
        doc = json.load(stream)
    incoming = Session.from_mapping(doc["incoming"])
    owned = Session.from_mapping(doc["owned"]) if doc.get("owned") is not None else None
    for name in ("foreign", "partial"):
        if type(doc.get(name, False)) is not bool:
            raise ValueError(f"{name} must be a boolean")
    print(json.dumps({
        "event": args.event,
        "decision": decide(args.event, incoming, owned, doc.get("foreign", False), doc.get("partial", False)),
        "network_modified": False,
        "production_activation_enabled": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
