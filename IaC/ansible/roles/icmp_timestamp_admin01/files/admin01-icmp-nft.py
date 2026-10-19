#!/usr/bin/env python3
"""Strictly scoped controller ICMP type-13 rule. No nftables.service manipulation."""
import os
import subprocess
import sys

TABLE = "homelab_icmp_timestamp"
EXPECTED = "192.168.2.48/24"
RULE = 'ip protocol icmp icmp type timestamp-request counter drop comment "homelab-icmp-admin01"'


def command(*argv):
    return subprocess.run(argv, text=True, capture_output=True)


def require_identity():
    if open("/etc/hostname", encoding="utf-8").read().strip() != "admin-01":
        raise RuntimeError("Unexpected host")
    ips = command("/usr/sbin/ip", "-4", "-o", "addr", "show", "dev", "eth0")
    if ips.returncode or "inet " + EXPECTED not in ips.stdout:
        raise RuntimeError("Unexpected controller address")
    svc = command("systemctl", "is-active", "nftables.service")
    if svc.stdout.strip() != "inactive":
        raise RuntimeError("Stock nftables service unexpectedly active")


def table_status():
    result = command("/usr/sbin/nft", "-a", "list", "table", "inet", TABLE)
    if result.returncode:
        return None
    return result.stdout


def exact_owned_table():
    result = command("/usr/sbin/nft", "-j", "list", "table", "inet", TABLE)
    if result.returncode:
        raise RuntimeError("Cannot inspect owned table")
    import json
    entries = json.loads(result.stdout)["nftables"]
    objs = [e for e in entries if "metainfo" not in e]
    if len(objs) != 3:
        raise RuntimeError("Unexpected number of owned nft objects")
    if set(objs[0].get("table", {}).keys()) != {"family", "name", "handle"}:
        raise RuntimeError("Unexpected table fields")
    t = objs[0]["table"]
    if t["family"] != "inet" or t["name"] != TABLE:
        raise RuntimeError("Unexpected table identity")
    chain = objs[1].get("chain", {})
    if not (chain.get("family") == "inet" and chain.get("table") == TABLE
            and chain.get("name") == "input" and chain.get("type") == "filter"
            and chain.get("hook") == "input" and chain.get("prio") == 0
            and chain.get("policy") == "accept"):
        raise RuntimeError("Unexpected chain policy")
    rule = objs[2].get("rule", {})
    if rule.get("family") != "inet" or rule.get("table") != TABLE or rule.get("chain") != "input":
        raise RuntimeError("Unexpected rule owner")
    # Verify exact textual match for expected rule plus counter state.
    visible = table_status()
    if visible is None:
        raise RuntimeError("Missing active owned table")
    import re
    lines = [x.strip() for x in visible.splitlines() if "comment" in x]
    if len(lines) != 1 or not re.fullmatch(
        r'ip protocol icmp icmp type timestamp-request counter packets \d+ bytes \d+ drop comment "homelab-icmp-admin01" # handle \d+',
        lines[0],
    ):
        raise RuntimeError("Unexpected type-13 rule")
    return True


def run_apply():
    require_identity()
    existing = table_status()
    if existing is not None:
        exact_owned_table()
        print("ALREADY_PRESENT")
        return
    if command("/usr/sbin/nft", "list", "tables").stdout.strip():
        raise RuntimeError("Existing nftables tables require review")
    commands = """add table inet homelab_icmp_timestamp
add chain inet homelab_icmp_timestamp input { type filter hook input priority 0; policy accept; }
add rule inet homelab_icmp_timestamp input ip protocol icmp icmp type timestamp-request counter drop comment "homelab-icmp-admin01"
"""
    validation = subprocess.run(["/usr/sbin/nft", "-c", "-f", "-"], input=commands, text=True, capture_output=True)
    if validation.returncode:
        raise RuntimeError("nft syntax validation failed: " + validation.stderr)
    applied = subprocess.run(["/usr/sbin/nft", "-f", "-"], input=commands, text=True, capture_output=True)
    if applied.returncode:
        raise RuntimeError("nft rule application failed: " + applied.stderr)
    exact_owned_table()
    print("RULE_ADDED")


def run_rollback():
    require_identity()
    if table_status() is None:
        print("ALREADY_ABSENT")
        return
    exact_owned_table()
    result = command("/usr/sbin/nft", "delete", "table", "inet", TABLE)
    if result.returncode:
        raise RuntimeError("Unable to remove owned table")
    print("RULE_REMOVED")


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2 or sys.argv[1] not in ("apply", "rollback", "inspect"):
            raise RuntimeError("Expected apply, rollback or inspect")
        if sys.argv[1] == "apply":
            run_apply()
        elif sys.argv[1] == "rollback":
            run_rollback()
        else:
            require_identity()
            print("OWNED_TABLE_PRESENT=" + str(table_status() is not None))
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print("ADMIN01_ICMP_ERROR=" + str(exc), file=sys.stderr)
        sys.exit(1)
