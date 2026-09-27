#!/usr/bin/env python3
"""Create one Markdown page per discovered device, preserving editable notes.

Reads an existing private Gate 4 evidence directory. Auto-generated pages
may be refreshed at any time; human-maintained notes live in separate files
and are never overwritten. Do not publish raw pages containing internal IPs,
MAC addresses, service versions or personal-device details to public Git.
"""
import argparse
import ipaddress
import json
from pathlib import Path
import re
import sys


def safe_slug(value):
    slug = re.sub(r"[^a-z0-9-]+", "-", str(value).strip().lower()).strip("-")
    if not slug or len(slug) > 110:
        raise ValueError("Invalid device identifier")
    return slug


def fenced_text(value):
    return str(value or "").replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def stable_id(host, expected):
    """A known inventory ID, observed MAC or IP persists across scans."""
    ip = host["ip"]
    if ip in expected:
        return safe_slug(expected[ip]["name"])
    mac = host.get("mac")
    if mac:
        return "mac-" + safe_slug(mac)
    return "ip-" + safe_slug(ip)


def new_notes(name):
    return f"""# {name} — editable notes

> These notes are maintained by you, not the scanner. Rerunning catalogue
> generation preserves this file exactly. Keep passwords, API tokens,
> recovery keys and other secrets OUT of Markdown.

## Identification
- Friendly name:
- What is this device?
- Manufacturer/model:
- Serial number (private reference, if needed):
- Owner:
- Physical location or virtualisation host:
- Assigned VLAN/network:

## Purpose and connections
- Why is it on the network?
- Criticality:
- Dependencies and related devices:
- Expected communication and exposed services:

## Administration
- Management URL or method:
- Configuration repository/documentation:
- Patching and maintenance:
- Planned retirement/replacement:

## Security, monitoring and recovery
- Expected firewall or access policy:
- Monitoring and alerts:
- Backup schedule:
- Last tested restore:
- Known issues or accepted risks:

## Notes and change history
- Date / observation:
"""


def render_device(host, asset, facts, notes_rel, scan_time):
    ip = host["ip"]
    ports = host.get("open_ports") or []
    discovered_name = ", ".join(host.get("names") or []) or "Not resolved"
    title = asset["name"] if asset else (host.get("names") or [ip])[0]
    details = [
        f"# {fenced_text(title)}",
        "",
        "**Evidence:** automatically generated from the Gate 4 scan; "
        "edit the linked notes file instead of this page.",
        "",
        f"**Last scan:** {fenced_text(scan_time)}  ",
        f"**IP:** \`{fenced_text(ip)}\`  ",
        f"**MAC:** \`{fenced_text(host.get('mac') or 'Not observed')}\`  ",
        f"**Discovered hostname:** {fenced_text(discovered_name)}  ",
        f"**Inventory identity:** {fenced_text(asset['name'] if asset else 'Undocumented / investigate')}  ",
        f"**Inventory role:** {fenced_text(asset['role'] if asset else 'Unverified')}  ",
        f"**Live discovery:** Responded to the scan  ",
        f"**Your editable notes:** [Open notes]({notes_rel})",
        "",
        "## Scan-observed open TCP ports",
        "",
        "The scan probes a selected TCP port list; unlisted ports are **not** "
        "verified closed. Service and version guesses require confirmation.",
        "",
        "| Port | Service | Product | Version |",
        "|---:|---|---|---|",
    ]
    if ports:
        for p in sorted(ports, key=lambda p: (p.get("protocol", ""), int(p["port"]))):
            details.append(
                f"| {p.get('port')}/{fenced_text(p.get('protocol'))} | "
                f"{fenced_text(p.get('service'))} | "
                f"{fenced_text(p.get('product'))} | "
                f"{fenced_text(p.get('version'))} |"
            )
    else:
        details.append("| No open ports identified in scanned set | — | — | — |")
    details += ["", "## Installed-state evidence", ""]
    if facts:
        details += [
            f"- OS: {fenced_text(facts.get('distribution', 'Unknown'))} "
            f"{fenced_text(facts.get('distribution_version', ''))}",
            f"- Kernel: \`{fenced_text(facts.get('kernel', 'Unknown'))}\`",
            f"- Observed hostname: \`{fenced_text(facts.get('observed_hostname', 'Unknown'))}\`",
            f"- Installed package records: {len(facts.get('packages', []))}",
            f"- Systemd unit-file records: {len(facts.get('unit_files', []))}",
            f"- Docker listing records: {len(facts.get('docker_containers', []))}",
            "- Full raw evidence: see the corresponding private "
            "\`managed-hosts/\` JSON file.",
        ]
    else:
        details.append(
            "No managed-host facts collected for this device. "
            "OS, software, systemd and Docker details remain unverified."
        )
    details += [
        "", "## Documentation review", "",
        f"- Canonical inventory: {'Matched by IP' if asset else 'No active inventory entry at this IP'}",
        "- Compare observed ports/software with CURRENT-STATE.md and Ansible.",
        "- Confirm identity, purpose and expected access before changing anything.",
        "- A responding device may be an ordinary household client rather than a managed host.",
        "", "## Your notes", "",
        f"[Edit this device's notes]({notes_rel})", "",
    ]
    return "\n".join(details)


def build(evidence, repo):
    report = json.loads((evidence / "network-scan.json").read_text())
    assets = json.loads((repo / "IaC/inventory/estate.json").read_text())["assets"]
    expected = {x["address"]: x for x in assets
                if x.get("address") and x.get("state") == "active"}
    facts_dir = evidence / "managed-hosts"
    facts = {p.stem: json.loads(p.read_text())
             for p in facts_dir.glob("*.json")} if facts_dir.exists() else {}
    catalogue = evidence / "device-catalogue"
    pages = catalogue / "devices"
    notes = catalogue / "notes"
    pages.mkdir(parents=True, exist_ok=True, mode=0o700)
    notes.mkdir(parents=True, exist_ok=True, mode=0o700)
    index = [
        "# Discovered network devices",
        "",
        f"Scan evidence: {report['scan_time']}. Source: {report['scan_source']}.",
        "",
        "This is a private catalogue: internal IPs, MACs and service versions are "
        "not suitable for an unrestricted public website or repository.",
        "",
        "Open each device page to inspect scan evidence; use its separate "
        "**notes** link for your own details. Re-running the generator "
        "refreshes auto-generated pages while preserving your notes.",
        "",
        "| Device | IP | Inventory | Notes |",
        "|---|---|---|---|",
    ]
    seen = set()
    hosts = report["hosts"]
    for host in sorted(hosts, key=lambda h: int(ipaddress.IPv4Address(h["ip"]))):
        asset = expected.get(host["ip"])
        slug = stable_id(host, expected)
        if slug in seen:
            raise ValueError(f"Duplicate stable device ID: {slug}")
        seen.add(slug)
        note_path = notes / f"{slug}.md"
        if not note_path.exists():
            name = asset["name"] if asset else host["ip"]
            note_path.write_text(new_notes(name))
            note_path.chmod(0o600)
        page = pages / f"{slug}.md"
        identity = asset["name"] if asset else "Unverified"
        fact = facts.get(asset["name"]) if asset else None
        page.write_text(render_device(
            host, asset, fact, f"../notes/{slug}.md", report["scan_time"]))
        page.chmod(0o600)
        index.append(
            f"| [{fenced_text(identity if asset else host['ip'])}](devices/{slug}.md) | "
            f"\`{fenced_text(host['ip'])}\` | "
            f"{'Documented' if asset else 'Investigate'} | "
            f"[Edit](notes/{slug}.md) |"
        )
    not_seen = [(ip, x["name"]) for ip, x in expected.items()
                if ip not in {h["ip"] for h in hosts}]
    index.extend(["", "## Documented assets not observed in this scan", ""])
    index.extend(
        ["This does not prove the device is offline; another probe or "
         "management-plane check may be needed.", ""]
    )
    if not_seen:
        index += [f"- {name} (\`{ip}\`)" for ip, name in sorted(not_seen)]
    else:
        index.append("None.")
    (catalogue / "README.md").write_text("\n".join(index) + "\n")
    (catalogue / "README.md").chmod(0o600)
    return catalogue, len(seen), len(not_seen)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("evidence_dir", type=Path,
                   help="EVIDENCE_DIRECTORY printed by the existing network scan")
    args = p.parse_args()
    evidence = args.evidence_dir.resolve()
    repo = Path(__file__).resolve().parents[3]
    directory, found, not_seen = build(evidence, repo)
    print("DEVICE_CATALOGUE=PASS")
    print(f"CATALOGUE_INDEX={directory / 'README.md'}")
    print(f"DEVICE_PAGES={found}")
    print(f"DOCUMENTED_NOT_OBSERVED={not_seen}")
    print("NOTES_PRESERVED=YES")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"DEVICE_CATALOGUE=FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
