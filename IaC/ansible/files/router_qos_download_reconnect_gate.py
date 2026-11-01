#!/usr/bin/env python3
"""Side-effect-free PPP reconnect recovery gate.

Integrates the ownership decision with PPP session transitions. This is not a
production actuator: it never invokes tc/ip, creates markers, or deletes links.
Snapshots are untrusted inputs; an approval is only a proposal for a later
independently verified executor.
"""
from dataclasses import dataclass
from typing import Any, Mapping
from router_qos_download_ownership import decide


@dataclass(frozen=True)
class RecoveryPlan:
    decision: str
    reason: str


def plan_reconnect(owner: Mapping[str, Any] | None,
                   current: Mapping[str, Any],
                   previous_session: Mapping[str, Any] | None) -> RecoveryPlan:
    if not isinstance(current, dict):
        return RecoveryPlan("preserve", "no current session snapshot")
    if current.get("event") != "up" or current.get("interface") != "ppp0":
        return RecoveryPlan("ignore", "not a managed PPP up event")
    if type(current.get("ppp_ifindex")) is not int or current["ppp_ifindex"] <= 0:
        return RecoveryPlan("preserve", "invalid current PPP identity")
    if previous_session is None:
        return RecoveryPlan("preserve", "previous PPP session unverified")
    if not isinstance(previous_session, dict):
        return RecoveryPlan("preserve", "invalid previous session")
    if previous_session.get("interface") != "ppp0":
        return RecoveryPlan("preserve", "unmanaged previous PPP identity")
    old = previous_session.get("ppp_ifindex")
    if type(old) is not int or old <= 0:
        return RecoveryPlan("preserve", "invalid previous PPP ifindex")
    if old == current["ppp_ifindex"]:
        return RecoveryPlan("preserve", "same PPP ifindex cannot prove new session")
    if current.get("old_session_confirmed_gone") is not True:
        return RecoveryPlan("preserve", "old PPP session teardown unverified")
    observed = current.get("kernel")
    if not isinstance(observed, dict):
        return RecoveryPlan("preserve", "missing authoritative kernel observation")
    result = decide(owner, observed)
    if result.action != "cleanup_proposed":
        return RecoveryPlan("preserve", result.reason)
    return RecoveryPlan("cleanup_proposed", "reconnected PPP with verified orphan identity; executor still required")


if __name__ == "__main__":
    raise SystemExit("Pure module; no production executable action")
