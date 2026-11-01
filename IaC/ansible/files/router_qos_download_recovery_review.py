#!/usr/bin/env python3
"""Read-only integration of the download QoS reconnect evidence chain.

This evaluates independently supplied observations and durable ownership data.
It NEVER invokes ip/tc mutations, reinstalls CAKE, or deletes IFBs.
A cleanup_proposed result is NOT authorisation to mutate production networking.
"""
from __future__ import annotations
from pathlib import Path
from typing import Callable
from router_qos_download_owner_record import load
from router_qos_download_observe import observe
from router_qos_download_reconnect_gate import plan_reconnect, RecoveryPlan


def review_reconnect(owner_path: str | Path, current: dict, previous: dict | None,
                     run: Callable, read_text: Callable,
                     other_users_verified: bool | None = None) -> RecoveryPlan:
    try:
        owner = load(owner_path)
    except (OSError, ValueError, KeyError, TypeError):
        return RecoveryPlan("preserve", "ownership record absent or invalid")
    try:
        observed = observe(run, read_text, other_users_verified)
    except (OSError, ValueError, TypeError, KeyError):
        return RecoveryPlan("preserve", "kernel observation failed")
    if not isinstance(current, dict):
        return RecoveryPlan("preserve", "current session invalid")
    event = dict(current)
    event["kernel"] = observed  # never trust caller-supplied kernel claims
    return plan_reconnect(owner, event, previous)


if __name__ == "__main__":
    raise SystemExit("Read-only integration library; no deployment entrypoint")
