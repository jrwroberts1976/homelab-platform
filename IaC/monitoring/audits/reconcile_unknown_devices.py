#!/usr/bin/env python3
"""Reconcile ONLY unresolved LAN devices against existing, private evidence.

Read-only input: Gate 4 network-scan.json, os-fingerprints.json, estate.json,
managed-hosts/*.json, optionally dns-clues.json and an IEEE OUI CSV.
No network probes, DNS database access, inventory mutation or notification
takes place here. A scheduler may refresh the inputs separately.
"""
import argparse
import csv
import ipaddress
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone


def load_json(path, default=None):
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text())


def manufacturer(mac, registry):
    cleaned = (mac or "").replace(":", "").replace("-", "").upper()
    if len(cleaned) != 12:
        return {"type": "unobserved", "name": None}
    try:
        first = int(cleaned[:2], 16)
    except ValueError:
        return {"type": "invalid", "name": None}
    if first & 2:
        return {"type": "locally_administered", "name": None}
    name = registry.get(cleaned[:6])
    return {"type": "registered_prefix" if name else "unknown_prefix",
            "name": name}


def load_oui(path):
    if not path:
        return {}
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return {r["Assignment"].upper(): r["Organization Name"]
                for r in csv.DictReader(fh)}


def load_dns(path):
    # Optional, already aggregated per-client and per-server; never include full query logs.
    data = load_json(path, default=[])
    if not isinstance(data, list):
        raise ValueError("dns-clues.json must be a list")
    grouped = {}
    for item in data:
        ip = item["ip"]
        server = item["server"]
        if server not in ("dns-01", "dns-02"):
            raise ValueError("Unexpected DNS source")
        domains = item.get("top_domains", [])
        if not isinstance(domains, list):
            raise ValueError("Invalid DNS domain summary")
        grouped.setdefault(ip, []).append({
            "server": server,
            "query_count": int(item.get("query_count", 0)),
            "top_domains": [str(domain) for domain in domains[:5]],
        })
    return grouped


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix="." + path.name + ".")
    try:
        with os.fdopen(fd, "w") as file:
            json.dump(data, file, indent=2)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        os.chmod(name, 0o600)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def reconcile(evidence, estate, dns=None, oui=None):
    network = load_json(evidence / "network-scan.json")
    scan = {h["ip"]: h for h in network["hosts"]}
    if network.get("subnet") != "192.168.2.0/24":
        raise ValueError("Refusing unexpected scan scope")
    expected = {asset["address"]: asset for asset in estate["assets"]
                if asset.get("state") == "active" and asset.get("address")}
    fingerprints = {x["ip"]: x for x in
                    load_json(evidence / "os-fingerprints.json", default=[])}
    facts_dir = evidence / "managed-hosts"
    facts = {p.stem for p in facts_dir.glob("*.json")} if facts_dir.exists() else set()
    dns_data = load_dns(dns) if dns else {}
    registry = load_oui(oui)
    resolved, unresolved = [], []
    for ip in sorted(scan, key=ipaddress.ip_address):
        host = scan[ip]
        asset = expected.get(ip)
        fingerprint = fingerprints.get(ip, {})
        matches = fingerprint.get("matches", [])
        direct_os = bool(asset and asset["name"] in facts)
        # Documented assets have an established identity even when Nmap is silent.
        # An Nmap candidate ALONE never confirms an undocumented device.
        established = bool(asset)
        entry = {
            "ip": ip,
            "mac": host.get("mac"),
            "known_identity": asset["name"] if asset else None,
            "direct_os_evidence": direct_os,
            "os_fingerprint_present": bool(matches),
            "top_os_candidates": matches[:3],
            "mac_manufacturer": manufacturer(host.get("mac"), registry),
            "discovery_names": host.get("names", []),
            "open_ports": host.get("open_ports", []),
            "dns_clues": dns_data.get(ip, []),
            "classification": ("documented" if established else
                               "unresolved_identity"),
        }
        (resolved if established else unresolved).append(entry)
    # Preserve uncertain OS information without promoting it to a fact.
    no_os = [x["ip"] for x in resolved + unresolved
             if not x["direct_os_evidence"] and not x["os_fingerprint_present"]]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "192.168.2.0/24",
        "known_devices": resolved,
        "unresolved_devices": unresolved,
        "no_direct_or_nmap_os_evidence": no_os,
        "counts": {
            "discovered": len(scan),
            "known": len(resolved),
            "unresolved": len(unresolved),
            "no_os_evidence": len(no_os),
        },
        "policy": "Never infer exact identity from OUI, DNS domains or Nmap alone.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("evidence", type=Path)
    p.add_argument("--estate", type=Path, required=True)
    p.add_argument("--dns", type=Path, help="Optional private DNS summary JSON")
    p.add_argument("--oui", type=Path, help="Optional downloaded IEEE oui.csv")
    p.add_argument("--output", type=Path,
                   help="Defaults to evidence/unresolved-devices.json")
    args = p.parse_args()
    report = reconcile(args.evidence, load_json(args.estate), args.dns, args.oui)
    output = args.output or args.evidence / "unresolved-devices.json"
    atomic_json(output, report)
    c = report["counts"]
    print(f"DISCOVERED={c['discovered']} KNOWN={c['known']} "
          f"UNRESOLVED={c['unresolved']} NO_OS_EVIDENCE={c['no_os_evidence']}")
    print(f"PRIVATE_REPORT={output}")


if __name__ == "__main__":
    main()
