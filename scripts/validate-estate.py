#!/usr/bin/env python3
"""Validate homelab estate identity, addressing and documentation drift.

This intentionally uses only the Python standard library so it can run on
GitHub-hosted runners and admin-01 without installing dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "IaC/inventory/estate.json"
CURRENT_STATE = ROOT / "docs/architecture/CURRENT-STATE.md"
ANSIBLE_INVENTORY = ROOT / "IaC/ansible/inventory/hosts.yml"
AUTHORITY_MARKER = "<!-- estate-authority: IaC/inventory/estate.json -->"
HISTORICAL_MARKER = "<!-- historical -->"
DOC_ROOTS = ("docs/", "runbooks/", "production docs/")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def load_inventory() -> dict:
    with INVENTORY.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_inventory(data: dict, errors: list[str]) -> None:
    assets = data.get("assets", [])
    planned = data.get("planned_assets", [])
    retired = data.get("retired_identities", [])

    names: set[str] = set()
    addresses: set[str] = set()

    for asset in assets:
        name = asset.get("name")
        address = asset.get("address")
        if not name or not address:
            fail(errors, f"active asset missing name/address: {asset!r}")
            continue
        if name.lower() in {n.lower() for n in names}:
            fail(errors, f"duplicate active asset name: {name}")
        if address in addresses:
            fail(errors, f"duplicate active asset address: {address}")
        names.add(name)
        addresses.add(address)

    for asset in planned:
        name = asset.get("name")
        address = asset.get("address")
        if not name or not address:
            fail(errors, f"planned asset missing name/address: {asset!r}")
            continue
        if name.lower() in {n.lower() for n in names}:
            fail(errors, f"planned asset collides with active asset name: {name}")
        if address in addresses:
            fail(errors, f"planned asset collides with active address: {address}")

    active_lower = {name.lower() for name in names}
    for item in retired:
        token = str(item.get("token", "")).strip()
        if not token:
            fail(errors, f"retired identity missing token: {item!r}")
        elif token.lower() in active_lower:
            fail(errors, f"retired token is also an active asset name: {token}")


def parse_current_state_active_table() -> dict[str, str]:
    text = CURRENT_STATE.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^## Active estate\s*$\n(.*?)(?=^##\s)", text)
    if not match:
        return {}

    rows: dict[str, str] = {}
    for raw in match.group(1).splitlines():
        line = raw.strip()
        if not line.startswith("|") or "`192.168." not in line:
            continue
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        label, address = cells[0], cells[1]
        if re.fullmatch(r"192\.168\.\d+\.\d+", address):
            rows[address] = label
    return rows


def validate_current_state(data: dict, errors: list[str]) -> None:
    rows = parse_current_state_active_table()
    if not rows:
        fail(errors, "could not parse the Active estate table in CURRENT-STATE.md")
        return

    expected_addresses = {asset["address"] for asset in data["assets"]}
    documented_addresses = set(rows)

    for asset in data["assets"]:
        address = asset["address"]
        expected_label = asset.get("document_label", asset["name"])
        actual_label = rows.get(address)
        if actual_label is None:
            fail(errors, f"CURRENT-STATE.md is missing active asset {asset['name']} at {address}")
        elif actual_label != expected_label:
            fail(
                errors,
                f"CURRENT-STATE.md label mismatch at {address}: "
                f"expected {expected_label!r}, found {actual_label!r}",
            )

    unexpected = documented_addresses - expected_addresses
    for address in sorted(unexpected):
        fail(errors, f"CURRENT-STATE.md lists {rows[address]!r} at {address}, but estate.json does not")


def parse_ansible_hosts() -> dict[str, str]:
    hosts: dict[str, str] = {}
    current_name: str | None = None
    current_indent = -1

    for raw in ANSIBLE_INVENTORY.read_text(encoding="utf-8").splitlines():
        host_match = re.match(r"^(\s{8,})([A-Za-z0-9_.-]+):\s*(?:\{\})?\s*$", raw)
        if host_match:
            current_indent = len(host_match.group(1))
            current_name = host_match.group(2)
            continue

        ip_match = re.match(r"^(\s+)ansible_host:\s*([^\s#]+)", raw)
        if ip_match and current_name and len(ip_match.group(1)) > current_indent:
            address = ip_match.group(2)
            previous = hosts.get(current_name)
            if previous and previous != address:
                raise ValueError(
                    f"Ansible inventory gives {current_name} conflicting addresses: {previous}, {address}"
                )
            hosts[current_name] = address
    return hosts


def validate_ansible(data: dict, errors: list[str]) -> None:
    try:
        hosts = parse_ansible_hosts()
    except ValueError as exc:
        fail(errors, str(exc))
        return

    for asset in data["assets"]:
        if not asset.get("managed_by_ansible"):
            continue
        name = asset["name"]
        expected_address = asset["address"]
        actual_address = hosts.get(name)
        if actual_address is None:
            fail(errors, f"Ansible inventory is missing managed active asset {name}")
        elif actual_address != expected_address:
            fail(
                errors,
                f"Ansible address mismatch for {name}: estate.json={expected_address}, "
                f"hosts.yml={actual_address}",
            )


def git_output(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT
    )


def changed_markdown_files(base: str, head: str) -> list[tuple[str, str]]:
    output = git_output("diff", "--name-status", base, head)
    changed: list[tuple[str, str]] = []
    for raw in output.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("\t")
        status = parts[0]
        path = parts[-1]
        if path.lower().endswith(".md"):
            changed.append((status, path))
    return changed


def validate_new_document_markers(base: str, head: str, errors: list[str]) -> None:
    for status, path in changed_markdown_files(base, head):
        if not status.startswith("A") or not path.startswith(DOC_ROOTS):
            continue
        doc = ROOT / path
        if not doc.exists():
            continue
        head_lines = "\n".join(doc.read_text(encoding="utf-8").splitlines()[:40])
        if AUTHORITY_MARKER not in head_lines:
            fail(
                errors,
                f"new operational/design document {path} must include {AUTHORITY_MARKER} "
                "within its first 40 lines",
            )


def validate_added_lines(base: str, head: str, data: dict, errors: list[str]) -> None:
    diff = git_output("diff", "--unified=0", base, head, "--", "*.md")
    current_file = ""
    retired_tokens = [item["token"] for item in data.get("retired_identities", [])]

    for raw in diff.splitlines():
        if raw.startswith("+++ b/"):
            current_file = raw[6:]
            continue
        if not raw.startswith("+") or raw.startswith("+++"):
            continue

        added = raw[1:]
        lowered = added.lower()
        for token in retired_tokens:
            if token.lower() not in lowered:
                continue
            if HISTORICAL_MARKER in added:
                continue
            fail(
                errors,
                f"{current_file}: new reference to retired identity/address {token!r} must either be "
                f"replaced with the current identity or explicitly marked {HISTORICAL_MARKER}",
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", help="base commit for changed-document checks")
    parser.add_argument("--head", help="head commit for changed-document checks")
    args = parser.parse_args()

    if bool(args.base) != bool(args.head):
        parser.error("--base and --head must be supplied together")

    errors: list[str] = []
    data = load_inventory()

    validate_inventory(data, errors)
    validate_current_state(data, errors)
    validate_ansible(data, errors)

    if args.base and args.head:
        try:
            validate_new_document_markers(args.base, args.head, errors)
            validate_added_lines(args.base, args.head, data, errors)
        except subprocess.CalledProcessError as exc:
            fail(errors, f"git diff validation failed: {exc.output.strip()}")

    if errors:
        print("ESTATE VALIDATION: FAIL", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1

    print("ESTATE VALIDATION: PASS")
    print(f"- active assets: {len(data['assets'])}")
    print(f"- planned assets: {len(data.get('planned_assets', []))}")
    print(f"- retired identities/addresses guarded: {len(data.get('retired_identities', []))}")
    if args.base and args.head:
        print(f"- changed-document guard: {args.base[:12]}..{args.head[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
