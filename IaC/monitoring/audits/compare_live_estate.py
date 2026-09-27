#!/usr/bin/env python3
"""Compare network/host evidence with canonical estate and architecture text.

No production access; reads only the report dir and the checked-out Git tree.
The result is an evidence-backed drift *candidate* register, not an automatic
claim of noncompliance. Historical architecture paragraphs are not treated
as current expected state; human review is required for software/port claims.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence_dir", type=Path)
    args = parser.parse_args()
    evidence = args.evidence_dir.resolve()
    if not evidence.is_dir():
        raise ValueError("Evidence directory missing")
    repo = Path(__file__).resolve().parents[3]
    inventory = json.loads((repo / "IaC/inventory/estate.json").read_text())
    architecture = (repo / "docs/architecture/CURRENT-STATE.md").read_text()
    network = json.loads((evidence / "network-scan.json").read_text())
    managed_dir = evidence / "managed-hosts"
    captured = {p.stem: json.loads(p.read_text())
                for p in managed_dir.glob("*.json")} if managed_dir.exists() else {}
    assets = [a for a in inventory["assets"] if a.get("state") == "active"]
    observed_ips = {a["ip"] for a in network["hosts"]}
    candidates = []
    rows = []
    for asset in assets:
        name = asset["name"]
        ip = asset.get("address")
        host = captured.get(name)
        observed = next((h for h in network["hosts"] if h["ip"] == ip), None)
        if not observed:
            candidates.append({
                "host": name, "category": "unverified",
                "expected": f"Documented active at {ip}",
                "observed": "Not discovered by LAN ARP/ICMP",
                "evidence": "network-scan.json",
                "next_action": "Check offline status, firewall, network segment and other monitoring evidence; do not assume host is down.",
            })
        if asset.get("managed_by_ansible") and not host:
            candidates.append({
                "host": name, "category": "unverified",
                "expected": "Host is marked Ansible-managed",
                "observed": "No managed-host facts captured",
                "evidence": "managed-hosts/ missing or host unreachable",
                "next_action": "Inspect Ansible recap, SSH access and approved host availability.",
            })
        if host and host["observed_hostname"].lower() != name.lower():
            candidates.append({
                "host": name, "category": "possible_live_or_documentation_drift",
                "expected": f"Hostname {name}", "observed": host["observed_hostname"],
                "evidence": f"managed-hosts/{name}.json",
                "next_action": "Verify aliases and physical/virtual identity before changing configuration or documents.",
            })
        if host and host.get("default_ipv4", {}).get("address") not in (ip, None):
            candidates.append({
                "host": name, "category": "possible_live_or_documentation_drift",
                "expected": f"Management address {ip}",
                "observed": f"Default-route address {host['default_ipv4'].get('address')}",
                "evidence": f"managed-hosts/{name}.json",
                "next_action": "Confirm whether this is a legitimate secondary management interface.",
            })
        failures = [key for key, rc in (host or {}).get("probe_return_codes", {}).items()
                    if rc and not (key == "docker" and rc != 0)]
        if failures:
            candidates.append({
                "host": name, "category": "unverified",
                "expected": "Complete live facts",
                "observed": f"Failed probes: {', '.join(failures)}",
                "evidence": f"managed-hosts/{name}.json",
                "next_action": "Run supported read-only fallback probes; do not mistake unavailable data for absence.",
            })
        rows.append({
            "name": name, "ip": ip, "role": asset["role"],
            "kind": asset["kind"], "documented": name in architecture,
            "lan_discovered": bool(observed), "managed_evidence": bool(host),
            "os": (host or {}).get("distribution", "unverified"),
            "os_version": (host or {}).get("distribution_version", "unverified"),
            "kernel": (host or {}).get("kernel", "unverified"),
            "open_tcp_ports": [f"{p['port']}/{p['service']}" for p in
                               (observed or {}).get("open_ports", [])
                               if p.get("protocol") == "tcp"],
            "installed_package_count": len((host or {}).get("packages", [])),
            "unit_count": len((host or {}).get("unit_files", [])),
            "running_docker_lines": len((host or {}).get("docker_containers", [])),
        })
    for host in network["hosts"]:
        if host["ip"] not in {a.get("address") for a in assets}:
            candidates.append({
                "host": host["ip"], "category": "undocumented_observed_address",
                "expected": "Not present in canonical active estate",
                "observed": "Responded to LAN discovery",
                "evidence": "network-scan.json",
                "next_action": "Identify device through approved DHCP/ARP records and document it if managed; may be an ordinary client.",
            })
    # Operational single-owner facts are historical until collected by this
    # run. Do not assume the migration has stayed healthy indefinitely.
    report = {
        "audit_time": dt.datetime.now().astimezone().isoformat(),
        "repository_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True,
            text=True, check=True).stdout.strip(),
        "estate_validated_at": inventory.get("validated_at"),
        "network_scan_time": network["scan_time"],
        "documented_active_count": len(assets),
        "lan_discovered_count": network["discovered_count"],
        "managed_host_evidence_count": len(captured),
        "host_comparison": rows, "review_register": candidates,
        "limitations": [
            "Listening sockets from ss are not necessarily remotely reachable.",
            "Service/OS detection is heuristic; absent ports do not prove absence.",
            "Unreachable hosts, routers, appliances and Home Assistant may not support Ansible fact collection.",
            "Software versions and service/port ownership require line-by-line comparison with CURRENT-STATE.md, IaC roles and deployment guides before classifying drift.",
            "Network traffic scans do not establish firewall exposure to the internet.",
            "Backups and restores must be audited using independent job and actual restore evidence.",
            "This report does not automatically edit canonical documentation or production configurations.",
        ],
    }
    (evidence / "audit-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = [
        "# Gate 4 — Whole-estate live evidence versus canonical documentation",
        "",
        f"Audit: {report['audit_time']}",
        f"Repository: \`{report['repository_commit']}\`",
        f"Network scan: {network['scan_time']}",
        "",
        f"Documented active assets: **{len(assets)}**; LAN discovered: **{network['discovered_count']}**; "
        f"managed fact records: **{len(captured)}**. These counts measure different populations.",
        "",
        "## Per-asset evidence",
        "",
        "| Host | Management IP | LAN discovery | Host facts | OS | Observed TCP ports |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        ports = ", ".join(row["open_tcp_ports"]) or "None identified / not probed"
        os_label = f"{row['os']} {row['os_version']}" if row["managed_evidence"] else "Unverified"
        lines.append(f"| {row['name']} | {row['ip']} | "
                     f"{'Yes' if row['lan_discovered'] else 'No/unknown'} | "
                     f"{'Yes' if row['managed_evidence'] else 'No'} | "
                     f"{os_label} | {ports} |")
    lines += ["", "## Findings requiring review", ""]
    if not candidates:
        lines.append("No automatic identity/visibility candidates; software, ports, backup and diagrams still require manual review.")
    for i, finding in enumerate(candidates, 1):
        lines.append(f"{i}. **{finding['host']} — {finding['category']}**: "
                     f"{finding['observed']}. Expected: {finding['expected']}. "
                     f"Evidence: {finding['evidence']}. Follow-up: {finding['next_action']}")
    lines += ["", "## Pending human reconciliation", "",
              "Compare packages and versions, enabled/running services, observed listeners, containers, "
              "Proxmox guest placement, DNS, monitoring coverage, backup/restore evidence and all relevant "
              "IaC declarations against current (not dated-history) sections of CURRENT-STATE.md.",
              "Keep undocumented, expected/planned and unverified findings separate.",
              ""]
    (evidence / "audit-review.md").write_text("\n".join(lines))
    print("AUDIT_COMPARISON_GENERATED=PASS")
    print(f"EVIDENCE_DIRECTORY={evidence}")
    print(f"DOCUMENTED_ACTIVE_ASSETS={len(assets)}")
    print(f"MANAGED_FACT_RECORDS={len(captured)}")
    print(f"REVIEW_CANDIDATES={len(candidates)}")
    print("Read audit-review.md and review the raw private JSON before updating documentation.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"AUDIT_COMPARISON_FAILED={exc}", file=sys.stderr)
        sys.exit(1)
