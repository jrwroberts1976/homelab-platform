"""Safely associate a protected Proxmox guest snapshot with saved LAN discovery.

Pure read-only functions. The file is private and no MAC addresses or
credentials are logged. The API is NOT contacted by this module.
"""
import json
import os
from pathlib import Path
import re
import stat
import time

MAC = re.compile(r"^[0-9a-f]{2}(?::[0-9a-f]{2}){5}$")
NODES = frozenset(("PROXMOX", "Proxmox-2"))
KINDS = frozenset(("qemu", "lxc"))


def normalise_mac(value):
    if not isinstance(value, str):
        return ""
    candidate = value.strip().lower().replace("-", ":")
    return candidate if MAC.fullmatch(candidate) else ""


def load_snapshot(path, inventory, max_age_seconds=172800, now=None, owner_uid=0):
    """Return {MAC: minimal guest identity}, and aggregate-only validation.

    Fail closed on unexpected file type, permissions, schema, age, source,
    identity or MAC collisions. Pass owner_uid=os.getuid() for offline tests.
    """
    path = Path(path)
    file_stat = path.lstat()
    if not stat.S_ISREG(file_stat.st_mode):
        raise ValueError("Proxmox snapshot must be an ordinary file")
    if file_stat.st_uid != owner_uid or stat.S_IMODE(file_stat.st_mode) != 0o600:
        raise ValueError("Proxmox snapshot must be owned by root and mode 0600")
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or (
        document.get("schema_version") != 1
        or document.get("source") != "proxmox_cluster_api"
    ):
        raise ValueError("Unexpected Proxmox snapshot schema or provenance")
    generated = document.get("generated_at")
    now = int(time.time()) if now is None else now
    if type(generated) is not int or (
        generated > now + 300 or generated < now - max_age_seconds
    ):
        raise ValueError("Proxmox guest snapshot is stale or has an invalid timestamp")
    raw_guests = document.get("guests_by_mac")
    if not isinstance(raw_guests, dict) or not raw_guests:
        raise ValueError("Proxmox guest snapshot has no MAC mapping")
    if not isinstance(inventory, dict):
        raise ValueError("The staged LAN inventory must be an object")

    identities = {}
    for original_mac, guest in raw_guests.items():
        mac = normalise_mac(original_mac)
        if not mac or mac != original_mac or mac in identities:
            raise ValueError("Invalid or ambiguous MAC in Proxmox guest snapshot")
        if not isinstance(guest, dict):
            raise ValueError("Invalid guest record")
        if guest.get("source") != "proxmox_cluster_api":
            raise ValueError("Invalid guest record provenance")
        node = guest.get("node")
        kind = guest.get("guest_type")
        vmid = guest.get("vmid")
        name = guest.get("name")
        if (
            node not in NODES or kind not in KINDS
            or not isinstance(vmid, str) or not vmid.isdecimal()
            or int(vmid) < 1 or not isinstance(name, str) or len(name) > 255
        ):
            raise ValueError("Invalid Proxmox guest identity")
        identities[mac] = {
            "source": "proxmox_cluster_api",
            "node": node,
            "guest_type": kind,
            "vmid": vmid,
            "name": name,
        }

    lan_macs = {
        normalise_mac(entry.get("mac"))
        for entry in inventory.values()
        if isinstance(entry, dict)
    }
    lan_macs.discard("")
    matched = len(identities.keys() & lan_macs)
    if not matched:
        raise ValueError("Guest snapshot has no overlap with saved LAN inventory")
    counts = {
        "snapshot_age_seconds": max(0, now - generated),
        "snapshot_guest_macs": len(identities),
        "saved_lan_devices": len(inventory),
        "matched_guest_macs": matched,
        "unmatched_guest_macs": len(identities) - matched,
    }
    return identities, counts
