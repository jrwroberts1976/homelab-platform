#!/usr/bin/env python3
"""Read-only Proxmox cluster guest/MAC inspection on monitor-01.

Never starts Nmap, writes state, prints guest identities or disables TLS.
The token is provided only through environment variables populated from
the protected on-host file by the Ansible gate.
"""
import argparse
import json
import os
import re
import ssl
import urllib.parse
import urllib.request

NODES = {"PROXMOX": "192.168.2.70", "Proxmox-2": "192.168.2.71"}
CA_FILE = "/etc/homelab-network-hosts/proxmox-ca.pem"
MAC = re.compile(r"(?i)^[0-9a-f]{2}(?::[0-9a-f]{2}){5}$")
NIC_KEY = re.compile(r"^net[0-9]+$")
QEMU_MODELS = frozenset({
    "virtio", "e1000", "e1000e", "rtl8139",
    "vmxnet3", "ne2k_pci", "pcnet", "i82551", "i82557b", "i82559er",
})


def parse_nics(guest_type, config):
    """Extract only explicitly named NIC MAC fields, never arbitrary text."""
    addresses = []
    for key, value in config.items():
        if not NIC_KEY.fullmatch(key):
            continue
        if not isinstance(value, str):
            raise ValueError("A guest NIC configuration was not a string")
        matches = []
        for item in value.split(","):
            field, sep, raw = item.partition("=")
            if not sep:
                continue
            if (guest_type == "lxc" and field.lower() == "hwaddr") or (
                guest_type == "qemu" and field.lower() in QEMU_MODELS
            ):
                address = raw.strip().lower()
                if not MAC.fullmatch(address):
                    raise ValueError("A guest NIC contained an invalid MAC")
                matches.append(address)
        if len(matches) != 1:
            raise ValueError("A guest NIC has missing/ambiguous MAC identity")
        addresses.append(matches[0])
    return addresses


def get_json(node, endpoint, auth, context):
    if node not in NODES:
        raise ValueError("Unexpected Proxmox node in cluster resource listing")
    url = (
        f"https://{NODES[node]}:8006/api2/json"
        + endpoint
    )
    request = urllib.request.Request(
        url,
        headers={"Authorization": auth, "Accept": "application/json"},
    )
    with urllib.request.urlopen(
        request, timeout=12, context=context,
    ) as response:
        if response.status != 200:
            raise RuntimeError("Guest inventory API did not return HTTP 200")
        payload = json.load(response)
    if not isinstance(payload, dict) or "data" not in payload:
        raise ValueError("Invalid API response structure")
    return payload["data"]


def collect(fetch):
    """fetch(node, API path) -> data. Pure MAC/correlation logic for tests."""
    inventories = [
        fetch(node, "/cluster/resources?type=vm") for node in NODES
    ]
    for items in inventories:
        if not isinstance(items, list):
            raise ValueError("Cluster resource inventory was not a list")

    def identity(item):
        return (str(item.get("type")), str(item.get("vmid")),
                str(item.get("node")), bool(item.get("template")))

    primary = inventories[0]
    if len(primary) < 4 or sorted(map(identity, primary)) != sorted(
        map(identity, inventories[1])
    ):
        raise ValueError("Both node APIs must agree on visible guest identities")

    identities = {}
    checked = 0
    templates = 0
    running = 0
    per_node = {node: 0 for node in NODES}

    for guest in primary:
        node = guest.get("node")
        kind = guest.get("type")
        vmid = guest.get("vmid")
        if node not in NODES or kind not in ("qemu", "lxc"):
            raise ValueError("Unexpected guest type or cluster node")
        if not isinstance(vmid, int) or vmid <= 0:
            raise ValueError("Invalid guest ID")
        endpoint = (
            f"/nodes/{urllib.parse.quote(node, safe='')}/{kind}/{vmid}/config"
        )
        config = fetch(node, endpoint)
        if not isinstance(config, dict):
            raise ValueError("Guest config was not a mapping")
        checked += 1
        per_node[node] += 1

        # Templates may have reusable NIC identities: never attribute their
        # MAC addresses to a live device dashboard.
        if guest.get("template"):
            templates += 1
            continue

        macs = parse_nics(kind, config)
        if guest.get("status") == "running":
            running += 1
            if not macs:
                raise ValueError("A running guest has no readable NIC MAC")
        for mac in macs:
            if mac in identities:
                raise ValueError("Two active guest definitions share one MAC")
            # This mapping is intentionally NEVER logged; the read-only
            # preflight validates it without writing any inventory state.
            identities[mac] = {
                "source": "proxmox_api",
                "node": node,
                "guest_type": kind,
                "vmid": str(vmid),
                "name": str(guest.get("name") or config.get(
                    "hostname" if kind == "lxc" else "name", ""
                )),
            }

    if running < 2 or not all(per_node.values()) or len(identities) < 2:
        raise ValueError("Incomplete cluster-wide guest MAC evidence")
    return {
        "event": "proxmox_guest_preflight",
        "strict_tls": True,
        "writes": False,
        "cluster_resources": len(primary),
        "guest_configs_checked": checked,
        "running_guests": running,
        "templates_excluded": templates,
        "unique_guest_macs": len(identities),
        "configs_per_node": per_node,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", required=True,
        help="Read-only verification; no output file or side effects",
    )
    parser.parse_args()
    token_id = os.environ.get("PVE_TOKEN_ID", "")
    token_secret = os.environ.get("PVE_TOKEN_SECRET", "")
    if not token_id or not token_secret:
        raise SystemExit("Missing on-host read-only Proxmox API credentials")
    # Validates both the issuer chain and the actual requested IP in SAN.
    context = ssl.create_default_context(cafile=CA_FILE)
    auth = f"PVEAPIToken={token_id}={token_secret}"
    fetch = lambda node, endpoint: get_json(node, endpoint, auth, context)
    print(json.dumps(collect(fetch), sort_keys=True))


if __name__ == "__main__":
    main()
