#!/usr/bin/env python3
"""Approved low-rate, read-only discovery from monitor-01 via admin-01.

Run from the repository root on admin-01. SSH uses its existing test-proven
monitor-01 key; the output remains in a private local directory and NEVER
enters Git. Discovery uses local ARP+ICMP on the LAN. Version scans cover
a limited set of TCP service ports, avoid NSE scripts and rate-limit traffic.
Do not scan networks you do not own or administer.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import xml.etree.ElementTree as ET

SUBNET = "192.168.2.0/24"
TARGET = "james@192.168.2.52"
PORTS = ("21,22,23,25,53,80,111,139,443,445,554,631,853,1883,2049,"
         "2375,3000,3001,3306,3389,5000,5432,5672,5900,8000,8006,8080,"
         "8081,8443,8883,9090,9093,9100,9115,9200,9443,10050,10051,27017")


def remote_nmap(args, identity, timeout):
    cmd = ["ssh", "-T", "-o", "BatchMode=yes", "-o",
           "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=12",
           "-i", str(identity), TARGET,
           shlex.join(["sudo", "-n", "nmap", *args])]
    result = subprocess.run(cmd, capture_output=True, text=True,
                            timeout=timeout, check=False)
    if result.returncode:
        raise RuntimeError(f"monitor-01 Nmap returned exit {result.returncode}: "
                           + result.stderr[-1500:])
    try:
        root = ET.fromstring(result.stdout)
    except ET.ParseError as exc:
        raise RuntimeError("Nmap returned malformed XML") from exc
    if root.tag != "nmaprun":
        raise RuntimeError("Unexpected scan response")
    return root, result.stdout


def parse_hosts(root):
    hosts = []
    for h in root.findall("host"):
        status = h.find("status")
        if status is None or status.get("state") != "up":
            continue
        addresses = {a.get("addrtype"): a.get("addr")
                     for a in h.findall("address")}
        ip = addresses.get("ipv4")
        if not ip:
            continue
        names = [n.get("name") for n in h.findall("./hostnames/hostname")
                 if n.get("name")]
        ports = []
        for p in h.findall("./ports/port"):
            state = p.find("state")
            if state is None or state.get("state") != "open":
                continue
            service = p.find("service")
            ports.append({
                "protocol": p.get("protocol"),
                "port": int(p.get("portid")),
                "state": "open",
                "service": service.get("name", "") if service is not None else "",
                "product": service.get("product", "") if service is not None else "",
                "version": service.get("version", "") if service is not None else "",
            })
        hosts.append({"ip": ip, "mac": addresses.get("mac"),
                      "names": names, "open_ports": ports})
    return hosts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--identity", default=str(Path.home() / ".ssh/proxmox-automation"))
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--discovery-only", action="store_true",
                        help="Skip service probes and collect only reachable hosts")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    estate = json.loads((repo / "IaC/inventory/estate.json").read_text())
    expected = {a["address"]: a["name"] for a in estate["assets"]
                if a.get("state") == "active" and a.get("address")}
    timestamp = dt.datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    outdir = Path(args.output_dir or
                  f"/var/tmp/homelab-postcutover-audit-{timestamp}").resolve()
    if outdir.exists():
        raise RuntimeError("Output directory already exists; never overwrite earlier evidence")
    old_umask = os.umask(0o077)
    try:
        outdir.mkdir(parents=True, mode=0o700)
        discovery, raw = remote_nmap(
            ["-sn", "-PR", "-n", "-oX", "-", SUBNET], args.identity, 240)
        (outdir / "discovery.xml").write_text(raw)
        discovered = parse_hosts(discovery)
        ips = {x["ip"] for x in discovered}
        # Managed hosts may be ICMP/ARP-invisible, so explicitly probe the
        # documented addresses as well; unreachable is not evidence of absence.
        targets = sorted(ips | set(expected))
        scanned = []
        if targets and not args.discovery_only:
            for offset in range(0, len(targets), 24):
                chunk = targets[offset:offset + 24]
                result, raw = remote_nmap(
                    ["-sT", "-sV", "--version-light", "-T2", "-n",
                     "--max-retries", "1", "--max-rate", "100",
                     "--host-timeout", "120s", "--open", "-p", PORTS,
                     "-oX", "-", *chunk],
                    args.identity, 5400)
                (outdir / f"services-{offset//24+1:02d}.xml").write_text(raw)
                scanned.extend(parse_hosts(result))
        by_ip = {x["ip"]: x for x in discovered}
        for result in scanned:
            old = by_ip.get(result["ip"], result)
            old["open_ports"] = result["open_ports"]
            by_ip[result["ip"]] = old
        report = {
            "scan_time": dt.datetime.now().astimezone().isoformat(),
            "scan_source": "monitor-01/192.168.2.52",
            "subnet": SUBNET,
            "scan_scope": "LAN ARP discovery plus rate-limited selected TCP service ports",
            "ports_probed": PORTS if not args.discovery_only else None,
            "documented_active_count": len(expected),
            "discovered_count": len(discovered),
            "documented_not_discovered": [
                {"ip": ip, "name": name} for ip, name in sorted(expected.items())
                if ip not in ips],
            "discovered_not_documented": sorted(ips - set(expected)),
            "hosts": sorted(by_ip.values(), key=lambda x: tuple(map(int, x["ip"].split(".")))),
            "limits": ["An absent ARP response does not prove a host is down.",
                       "Only selected TCP ports were tested; absence is not a complete closed-port inventory.",
                       "Nmap service/version identification is heuristic.",
                       "Non-LAN and disconnected hosts require separate scope."],
        }
        (outdir / "network-scan.json").write_text(json.dumps(report, indent=2) + "\n")
        print("NETWORK_SCAN_COMPLETE=PASS")
        print(f"EVIDENCE_DIRECTORY={outdir}")
        print(f"LAN_DISCOVERED={len(discovered)}")
        print(f"DOCUMENTED_ACTIVE={len(expected)}")
        print(f"DOCUMENTED_NOT_DISCOVERED={len(report['documented_not_discovered'])}")
        print(f"UNDOCUMENTED_IPS={len(report['discovered_not_documented'])}")
        print("NEXT=Collect managed-host evidence and compare current docs against this scan.")
    finally:
        os.umask(old_umask)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"NETWORK_SCAN_FAILED={exc}", file=sys.stderr)
        sys.exit(1)
