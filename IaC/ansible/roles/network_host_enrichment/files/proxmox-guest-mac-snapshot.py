#!/usr/bin/env python3
"""Publish a root-only, MAC-keyed snapshot of read-only Proxmox guest identity.

No Nmap, no network inventory rewrite, no timer or Proxmox modifications.
Credentials come from the already installed root-only on-host environment;
strictly validate the pinned cluster CA and the API endpoint's IP SAN.
Only --publish creates a *new* snapshot; never overwrite an existing one.
Never log API credentials, MACs or full guest records.
"""
import argparse
import json
import os
from pathlib import Path
import re
import ssl
import stat
import tempfile
import time
import urllib.parse
import urllib.request

NODES = {"PROXMOX": "192.168.2.70", "Proxmox-2": "192.168.2.71"}
CA_PATH = "/etc/homelab-network-hosts/proxmox-ca.pem"
DEST = Path("/var/lib/homelab-network-hosts/proxmox-guests.json")
INVENTORY = Path("/var/lib/homelab-network-hosts/inventory.json")
MAC = re.compile(r"(?i)^[0-9a-f]{2}(?::[0-9a-f]{2}){5}$")
NIC_KEY = re.compile(r"net[0-9]+")
QEMU_NIC_MODELS = frozenset({
    "virtio", "e1000", "e1000e", "rtl8139", "vmxnet3",
    "ne2k_pci", "pcnet", "i82551", "i82557b", "i82559er",
})


def parse_macs(guest_type, config):
    macs = []
    for key, raw in config.items():
        if not NIC_KEY.fullmatch(key):
            continue
        if not isinstance(raw, str):
            raise ValueError("Invalid guest NIC configuration type")
        found = []
        for part in raw.split(","):
            field, sep, value = part.partition("=")
            if not sep:
                continue
            if (guest_type == "lxc" and field.lower() == "hwaddr") or (
                guest_type == "qemu" and field.lower() in QEMU_NIC_MODELS
            ):
                mac = value.strip().lower()
                if not MAC.fullmatch(mac):
                    raise ValueError("Malformed Proxmox guest MAC")
                found.append(mac)
        if len(found) != 1:
            raise ValueError("Guest NIC must identify exactly one valid MAC")
        macs.extend(found)
    if len(set(macs)) != len(macs):
        raise ValueError("Duplicate MAC on one guest")
    return macs


def fetch_api(node, endpoint, auth, context):
    if node not in NODES:
        raise ValueError("Unknown Proxmox node")
    request = urllib.request.Request(
        f"https://{NODES[node]}:8006/api2/json{endpoint}",
        headers={"Authorization": auth, "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, context=context, timeout=12) as res:
        if res.status != 200:
            raise ValueError("Proxmox API did not return HTTP 200")
        body = json.load(res)
    if not isinstance(body, dict) or "data" not in body:
        raise ValueError("Unexpected API response")
    return body["data"]


def inspect_inventory(path=INVENTORY):
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("Staged discovery inventory is not an object")
    macs = set()
    for record in data.values():
        if not isinstance(record, dict):
            continue
        raw = str(record.get("mac") or "").strip().lower().replace("-", ":")
        if MAC.fullmatch(raw):
            macs.add(raw)
    return macs


def collect(fetch, staged_macs):
    # Make sure the two independent node APIs agree before publishing.
    inventories = [fetch(node, "/cluster/resources?type=vm") for node in NODES]
    if not all(isinstance(items, list) for items in inventories):
        raise ValueError("Cluster inventory must be a list")

    def key(guest):
        return (
            str(guest.get("type")), str(guest.get("vmid")),
            str(guest.get("node")), bool(guest.get("template")),
            str(guest.get("status")),
        )

    primary, secondary = inventories
    if len(primary) < 4 or sorted(map(key, primary)) != sorted(
        map(key, secondary)
    ):
        raise ValueError("Cluster nodes disagree on guest inventory")
    if len({key(guest) for guest in primary}) != len(primary):
        raise ValueError("Duplicate cluster guest record")

    identities = {}
    per_node = dict.fromkeys(NODES, 0)
    running = templates = checked = 0

    for guest in primary:
        node = guest.get("node")
        kind = guest.get("type")
        vmid = guest.get("vmid")
        status = guest.get("status")
        if node not in NODES or kind not in ("lxc", "qemu"):
            raise ValueError("Unexpected node or guest type")
        if type(vmid) is not int or vmid < 1 or status not in ("running", "stopped"):
            raise ValueError("Invalid guest ID or state")

        endpoint = (
            f"/nodes/{urllib.parse.quote(node, safe='')}/{kind}/{vmid}/config"
        )
        config = fetch(node, endpoint)
        if not isinstance(config, dict):
            raise ValueError("Guest config is not an object")
        checked += 1
        per_node[node] += 1

        # VM templates may deliberately share reusable virtual NIC MACs.
        if guest.get("template"):
            templates += 1
            continue
        if status != "running":
            # Avoid associating a stopped machine with an online host.
            continue

        macs = parse_macs(kind, config)
        if not macs:
            raise ValueError("Running guest has no readable NIC MAC")
        running += 1
        name = str(guest.get("name") or config.get(
            "hostname" if kind == "lxc" else "name", ""
        ))
        for mac in macs:
            if mac in identities:
                raise ValueError("Duplicate running guest MAC across nodes")
            identities[mac] = {
                "source": "proxmox_cluster_api",
                "node": node,
                "guest_type": kind,
                "vmid": str(vmid),
                "name": name,
            }

    if running < 2 or len(identities) < 2 or not all(per_node.values()):
        raise ValueError("Incomplete cluster-wide guest inventory")

    matches = len(staged_macs & set(identities))
    if matches < 1:
        raise ValueError("No MAC overlap with the staged LAN inventory")

    now = int(time.time())
    document = {
        "schema_version": 1,
        "source": "proxmox_cluster_api",
        "generated_at": now,
        "cluster_resources": len(primary),
        "templates_excluded": templates,
        "guests_by_mac": identities,
    }
    summary = {
        "event": "proxmox_guest_snapshot",
        "strict_tls": True,
        "cluster_resources": len(primary),
        "configs_checked": checked,
        "running_guests": running,
        "templates_excluded": templates,
        "unique_guest_macs": len(identities),
        "matches_staged_mac_inventory": matches,
        "per_node_configs": per_node,
    }
    return document, summary


def publish_new(path, document):
    # Link a fully fsynced root-only temporary file atomically. os.link
    # fails if destination already exists, including a symlink; no replace.
    if path.exists() or path.is_symlink():
        raise FileExistsError("Guest snapshot already exists; do not overwrite")
    if not path.parent.is_dir():
        raise FileNotFoundError("Staged network state directory is missing")
    descriptor, temp_path = tempfile.mkstemp(
        prefix=".proxmox-guests.", dir=str(path.parent),
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            os.fchmod(handle.fileno(), 0o600)
            json.dump(document, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temp_path, path)
    finally:
        os.unlink(temp_path)


def verify_saved(path=DEST):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or (
        stat.S_IMODE(info.st_mode) != 0o600
    ):
        raise ValueError("Saved guest snapshot is not a root-only regular file")
    doc = json.loads(path.read_text(encoding="utf-8"))
    guests = doc.get("guests_by_mac")
    if doc.get("schema_version") != 1 or not isinstance(guests, dict):
        raise ValueError("Invalid guest snapshot schema")
    if not isinstance(doc.get("generated_at"), int):
        raise ValueError("Missing snapshot timestamp")
    if len(guests) < 2:
        raise ValueError("Guest snapshot has insufficient MAC records")
    if any(not MAC.fullmatch(mac) for mac in guests):
        raise ValueError("Guest snapshot contains invalid MAC identifiers")
    return {
        "event": "proxmox_guest_snapshot_verified",
        "saved_file_mode": "0600",
        "unique_guest_macs": len(guests),
        "age_seconds": max(0, int(time.time()) - doc["generated_at"]),
    }


def main():
    args = argparse.ArgumentParser(description=__doc__)
    mode = args.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--publish", action="store_true")
    mode.add_argument("--verify", action="store_true")
    opt = args.parse_args()
    if opt.verify:
        print(json.dumps(verify_saved(), sort_keys=True))
        return

    token_id = os.environ.get("PVE_TOKEN_ID", "")
    token_secret = os.environ.get("PVE_TOKEN_SECRET", "")
    if not token_id or not token_secret:
        raise ValueError("Protected API token is unavailable")
    context = ssl.create_default_context(cafile=CA_PATH)
    auth = f"PVEAPIToken={token_id}={token_secret}"
    fetch = lambda node, endpoint: fetch_api(node, endpoint, auth, context)
    document, summary = collect(fetch, inspect_inventory())
    if opt.publish:
        publish_new(DEST, document)
    summary["snapshot_created"] = bool(opt.publish)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
