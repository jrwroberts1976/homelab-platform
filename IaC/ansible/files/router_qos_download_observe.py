#!/usr/bin/env python3
"""Read-only production observation adapter for the download QoS recovery gate.

No tc/ip mutations. Ambiguous output is intentionally reported as unknown,
which the pure ownership gate refuses. Not an actuator or deployment playbook.
"""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path
from typing import Callable

IFB = "ifbqosdl0"
WAN = "ppp0"


def observe(run: Callable, read_text: Callable, other_users_verified: bool | None = None) -> dict:
    """Collect a conservative kernel snapshot.

    other_users_verified must originate from an independent ingress/redirect
    enumerator. Never guess False merely because ppp0 ingress looks clean.
    """
    boot = read_text("/proc/sys/kernel/random/boot_id").strip()
    ifindex_raw = read_text(f"/sys/class/net/{IFB}/ifindex").strip()
    ifindex = int(ifindex_raw) if ifindex_raw.isdecimal() and int(ifindex_raw) > 0 else None
    alias = run(["ip", "-j", "link", "show", "dev", IFB])
    try:
        links = json.loads(alias)
        if len(links) != 1 or links[0].get("ifname") != IFB:
            raise ValueError("ambiguous IFB")
        kernel_alias = links[0].get("ifalias", "")
        token = kernel_alias.removeprefix("router-qos-download:") if kernel_alias.startswith("router-qos-download:") else None
    except (ValueError, TypeError, KeyError):
        token = None
    cake = run(["tc", "qdisc", "show", "dev", IFB])
    exact_cake = (len([x for x in cake.splitlines() if x.startswith("qdisc cake ")]) == 1
                  and "bandwidth 43Mbit" in cake and "besteffort" in cake and "flows" in cake)
    upload = run(["tc", "qdisc", "show", "dev", "eth1"])
    filters = run(["tc", "filter", "show", "dev", WAN, "ingress"])
    root = run(["tc", "qdisc", "show", "dev", WAN])
    ppp = run(["ip", "-j", "link", "show", "dev", WAN])
    try:
        plinks = json.loads(ppp)
        ppp_present = len(plinks) == 1 and plinks[0].get("ifname") == WAN
    except (ValueError, TypeError):
        ppp_present = False
    return {
        "boot_id": boot,
        "ifb_name": IFB,
        "ifb_ifindex": ifindex,
        "kernel_alias_token": token,
        "qdisc": "cake-43mbit-besteffort-flows" if exact_cake else "unknown",
        "ppp_present": ppp_present,
        "ppp_ingress": "clean" if ppp_present and not filters.strip() and
                       not re.search(r"\b(clsact|ingress)\b", root) else "unknown",
        "upload": "cake-13mbit" if "qdisc cake " in upload and "bandwidth 13Mbit" in upload else "unknown",
        "other_ifb_users": other_users_verified if type(other_users_verified) is bool else None,
    }


def _run(argv):
    try:
        return subprocess.check_output(argv, text=True, timeout=5, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def _read(path):
    try:
        return Path(path).read_text()
    except (OSError, ValueError):
        return ""


if __name__ == "__main__":
    print(json.dumps(observe(_run, _read), sort_keys=True))
