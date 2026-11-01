#!/usr/bin/env python3
"""Offline-only model of recoverable legacy download QoS states.

This module never invokes ip, tc, systemd, or other commands. It deliberately
returns REFUSE for states requiring deletion/adoption of unverified resources.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class KernelState:
    ppp_present: bool
    upload_ok: bool
    ifb_present: bool
    ifb_verified_owned: bool
    ingress: str  # 'clean', 'legacy-exact', or 'foreign'
    owner_record_present: bool


def recovery_decision(s: KernelState) -> str:
    if not s.ppp_present or not s.upload_ok:
        return "REFUSE_BASELINE_CHANGED"
    if s.ingress == "foreign":
        return "REFUSE_FOREIGN_INGRESS"
    if s.ifb_present:
        if not s.ifb_verified_owned:
            return "REFUSE_UNVERIFIED_IFB"
        if s.ingress == "legacy-exact":
            return "PRESERVE_WORKING_DOWNLOAD"
        return "REFUSE_AMBIGUOUS_OWNED_IFB"
    if s.owner_record_present:
        return "REFUSE_STALE_OWNER_RECORD"
    if s.ingress != "clean":
        return "REFUSE_DANGLING_REDIRECT"
    return "CREATE_ONLY_RECOVERY_ELIGIBLE_NOT_AUTHORISED"


if __name__ == "__main__":
    raise SystemExit("Offline library only; no recovery execution entrypoint")
