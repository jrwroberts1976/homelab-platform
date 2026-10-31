#!/usr/bin/env python3
"""Offline watchdog attestation for the isolated executor.

A boolean configuration flag is NOT evidence that a watchdog exists.
This validator is deliberately read-only: it verifies a snapshot from a
future namespace-local watcher/runner. Never use simulated inputs to approve
production operation.
"""
from dataclasses import dataclass


class NotReady(RuntimeError):
    pass


@dataclass(frozen=True)
class WatchdogEvidence:
    namespace: str
    namespace_inode: int
    owned_inode: int
    unit: str
    timer_active: bool
    callback_path: str
    callback_exists: bool
    deadline_monotonic_us: int
    now_monotonic_us: int


def validate(evidence: WatchdogEvidence) -> None:
    if evidence.namespace != "qos-p5":
        raise NotReady("unexpected namespace")
    if evidence.namespace_inode <= 0 or evidence.namespace_inode != evidence.owned_inode:
        raise NotReady("namespace ownership mismatch")
    if evidence.unit != "qos-p5-rollback.timer" or not evidence.timer_active:
        raise NotReady("independent watchdog not armed")
    if evidence.callback_path != "/run/qos-p5-rollback.sh" or not evidence.callback_exists:
        raise NotReady("watchdog callback missing")
    if evidence.now_monotonic_us < 0 or evidence.deadline_monotonic_us <= evidence.now_monotonic_us:
        raise NotReady("watchdog deadline expired or invalid")


def authorized_operations(evidence: WatchdogEvidence):
    validate(evidence)
    return ("verify_source", "create_owned_ifb", "attach_cake", "attach_owned_redirect")


if __name__ == "__main__":
    raise SystemExit("Library only: no live watchdog activation implemented")
