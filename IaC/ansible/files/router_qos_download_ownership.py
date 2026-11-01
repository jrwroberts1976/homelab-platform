#!/usr/bin/env python3
"""Pure ownership decision for router download IFB, with no network side effects.

An owner record alone is not an authority to delete a kernel object. A caller
must supply independently gathered current kernel identity and configuration.
Only an exact, validated match permits a *proposed* orphan cleanup.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping
import re

BOOT_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
TOKEN_RE = re.compile(r"^[0-9a-f]{32}$")


@dataclass(frozen=True)
class Decision:
    action: str
    reason: str


def _positive_int(x: Any) -> bool:
    return type(x) is int and x > 0


def decide(owner: Mapping[str, Any] | None, actual: Mapping[str, Any]) -> Decision:
    """Return preserve/cleanup_proposed; never run ip, tc, or remove files.

    Both boot and IFB ifindex must match. The recorded install token must also
    be verified independently against a kernel-side alias to disallow a forged
    or stale disk record authorising teardown of an unrelated IFB.
    """
    if not isinstance(owner, dict):
        return Decision("preserve", "missing or invalid ownership record")
    if not isinstance(actual, dict):
        return Decision("preserve", "missing kernel observation")
    required = {"boot_id", "ifb_name", "ifb_ifindex", "token"}
    if set(owner) != required:
        return Decision("preserve", "unexpected ownership record fields")
    if not isinstance(owner["boot_id"], str) or not BOOT_RE.fullmatch(owner["boot_id"]):
        return Decision("preserve", "invalid boot ID")
    if owner["ifb_name"] != "ifbqosdl0" or not _positive_int(owner["ifb_ifindex"]):
        return Decision("preserve", "invalid recorded IFB identity")
    if not isinstance(owner["token"], str) or not TOKEN_RE.fullmatch(owner["token"]):
        return Decision("preserve", "invalid install token")
    if actual.get("boot_id") != owner["boot_id"]:
        return Decision("preserve", "boot changed")
    if actual.get("ifb_name") != owner["ifb_name"] or actual.get("ifb_ifindex") != owner["ifb_ifindex"]:
        return Decision("preserve", "IFB identity changed")
    if actual.get("kernel_alias_token") != owner["token"]:
        return Decision("preserve", "kernel alias token mismatch")
    if actual.get("qdisc") != "cake-43mbit-besteffort-flows":
        return Decision("preserve", "unexpected IFB qdisc")
    if actual.get("ppp_present") is not True or actual.get("ppp_ingress") != "clean":
        return Decision("preserve", "PPP ingress not confirmed clean")
    if actual.get("upload") != "cake-13mbit":
        return Decision("preserve", "upload shape changed")
    if actual.get("other_ifb_users") is not False:
        return Decision("preserve", "IFB users cannot be ruled out")
    return Decision("cleanup_proposed", "independent boot, IFB and kernel token match")


if __name__ == "__main__":
    raise SystemExit("Pure module only: import decide() from tests or reviewed controller")
