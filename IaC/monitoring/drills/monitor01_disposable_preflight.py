#!/usr/bin/env python3
"""READ-ONLY Gate 3 disposable-pair admission. Never runs a migration playbook.

Both disposable guests must have NO default route, no production-subnet route,
distinct machine IDs, unique non-production addresses and systemd. The
controller must already be able to SSH to their isolated bridge. Run this
before creating synthetic fixtures or using a disposable-only playbook copy.
"""
import argparse
import ipaddress
import json
import re
import subprocess
import sys

PRODUCTION = ipaddress.ip_network("192.168.2.0/24")
DEFAULT_LAB = ipaddress.ip_network("10.77.77.0/24")
SAFE_USERNAME = re.compile(r"^[a-z_][a-z0-9_-]{0,31}$")
PRODUCTION_NAMES = {"proxmox", "proxmox-2", "monitor-01", "admin-01"}


def check_candidate(address, lab=DEFAULT_LAB):
    ip = ipaddress.ip_address(address)
    if ip.version != 4 or ip not in lab or ip in PRODUCTION:
        raise ValueError("Drill IP must be IPv4 on the isolated, non-production lab network")
    return str(ip)


def validate_routes(routes, lab=DEFAULT_LAB):
    """Reject any IPv4 default or route that could reach production."""
    for route in routes:
        dest = route.get("dst", "default")
        if dest == "default":
            raise ValueError("Guest has a default route: isolation not demonstrated")
        network = ipaddress.ip_network(dest, strict=False)
        if network.version != 4:
            continue
        if network.overlaps(PRODUCTION):
            raise ValueError("Guest has a production-facing route")
        if route.get("gateway"):
            gateway = ipaddress.ip_address(route["gateway"])
            if gateway not in lab:
                raise ValueError("Guest route has a gateway outside isolated lab network")
    return True


def validate_guest(label, address, report, lab=DEFAULT_LAB):
    hostname = report["hostname"].strip().lower().split(".")[0]
    if hostname in PRODUCTION_NAMES or hostname != label:
        raise ValueError("Unexpected guest hostname or production identity")
    if not re.fullmatch(r"[a-f0-9]{32}", report["machine_id"].strip().lower()):
        raise ValueError("Invalid or missing machine-id")
    interfaces = json.loads(report["interfaces"])
    observed = {
        item["local"]
        for link in interfaces
        for item in link.get("addr_info", [])
        if item.get("family") == "inet"
    }
    if address not in observed:
        raise ValueError("Expected isolated IPv4 address not assigned to guest")
    if any(ipaddress.ip_address(x) in PRODUCTION for x in observed):
        raise ValueError("Guest exposes a production-subnet address")
    if any(ipaddress.ip_address(x) not in lab
           and not ipaddress.ip_address(x).is_loopback for x in observed):
        raise ValueError("Guest exposes an interface outside the lab network")
    routes = json.loads(report["routes"])
    validate_routes(routes, lab)
    if not report["systemd"].startswith("systemd "):
        raise ValueError("Disposable guest is not systemd-capable")
    return report["machine_id"].strip().lower()


def ssh_readonly(ip, user, identity):
    cmd = ["ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
           "-o", "ConnectTimeout=8", "-o", "ClearAllForwardings=yes"]
    if identity:
        cmd += ["-i", identity, "-o", "IdentitiesOnly=yes"]
    cmd.append(f"{user}@{ip}")
    # Fixed, read-only commands. No user input interpolated into remote script.
    remote = (
        "set -eu; "
        "hostname -s; "
        "cat /etc/machine-id; "
        "ip -j -4 addr show; "
        "ip -j -4 route show table all; "
        "systemctl --version | head -1"
    )
    result = subprocess.run(cmd + [remote], text=True, capture_output=True,
                            timeout=30, check=False)
    if result.returncode:
        raise RuntimeError(f"SSH read-only probe failed for {ip}: "
                           "verify key, host fingerprint, networking and guest dependencies")
    lines = result.stdout.splitlines()
    if len(lines) != 5:
        raise RuntimeError("Unexpected guest probe response; no drill permitted")
    return dict(zip(("hostname", "machine_id", "interfaces", "routes", "systemd"), lines))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Disposable drill-source IPv4")
    parser.add_argument("--target", required=True, help="Disposable drill-target IPv4")
    parser.add_argument("--user", default="james", help="Unprivileged SSH user")
    parser.add_argument("--identity", help="SSH private-key path for disposable guests")
    parser.add_argument("--lab-cidr", default=str(DEFAULT_LAB),
                        help="Private isolated lab CIDR, default 10.77.77.0/24")
    args = parser.parse_args(argv)
    try:
        lab = ipaddress.ip_network(args.lab_cidr, strict=True)
        if lab.version != 4 or not lab.is_private or lab.overlaps(PRODUCTION):
            raise ValueError("Lab network must be private IPv4 without production overlap")
        if not SAFE_USERNAME.fullmatch(args.user):
            raise ValueError("Invalid SSH user")
        source = check_candidate(args.source, lab)
        target = check_candidate(args.target, lab)
        if source == target:
            raise ValueError("Source and target must be separate disposable VMs")
        first = ssh_readonly(source, args.user, args.identity)
        second = ssh_readonly(target, args.user, args.identity)
        first_id = validate_guest("drill-source", source, first, lab)
        second_id = validate_guest("drill-target", target, second, lab)
        if first_id == second_id:
            raise ValueError("Identical machine-ids indicate cloned guests were not reseeded")
    except (ValueError, RuntimeError, subprocess.TimeoutExpired, OSError,
            json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"DISPOSABLE_PAIR_PREFLIGHT=FAIL: {exc}", file=sys.stderr)
        return 1
    print("DISPOSABLE_PAIR_PREFLIGHT=PASS")
    print(f"isolated_network={lab}")
    print(f"source={source} hostname=drill-source")
    print(f"target={target} hostname=drill-target")
    print("No data copied, services changed, playbooks executed or email sent.")
    print("HOLD: passing this check does not approve production or prove the actual cutover.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
