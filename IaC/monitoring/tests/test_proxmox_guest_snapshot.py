"""Offline tests for the standalone, non-overwriting PVE guest MAC snapshot."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "ansible/roles/network_host_enrichment/files/proxmox-guest-mac-snapshot.py"
)
spec = importlib.util.spec_from_file_location("pve_snapshot", SCRIPT)
snap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snap)


def mock_fetch(*, duplicate=False, disagrees=False, missing_mac=False):
    guests = [
        {"type": "qemu", "vmid": 200, "node": "PROXMOX",
         "status": "running", "name": "cloud-01", "template": 0},
        {"type": "lxc", "vmid": 101, "node": "Proxmox-2",
         "status": "running", "name": "dns-01", "template": 0},
        {"type": "qemu", "vmid": 201, "node": "PROXMOX",
         "status": "running", "name": "sensor-01", "template": 0},
        {"type": "qemu", "vmid": 9000, "node": "PROXMOX",
         "status": "stopped", "name": "template", "template": 1},
    ]
    configs = {
        ("PROXMOX", "qemu", 200): {
            "net0": "virtio=BC:24:11:AA:00:01,bridge=vmbr0"},
        ("Proxmox-2", "lxc", 101): {
            "net0": "name=eth0,bridge=vmbr0,hwaddr=52:54:00:00:00:02,type=veth"},
        ("PROXMOX", "qemu", 201): {
            "net0": "e1000=DE:AD:BE:EF:00:03,bridge=vmbr0"},
        ("PROXMOX", "qemu", 9000): {
            "net0": "virtio=BC:24:11:AA:00:01,bridge=vmbr0"},
    }
    if duplicate:
        configs[("PROXMOX", "qemu", 201)]["net0"] = (
            "virtio=BC:24:11:AA:00:01,bridge=vmbr0"
        )
    if missing_mac:
        configs[("Proxmox-2", "lxc", 101)]["net0"] = (
            "name=eth0,bridge=vmbr0,type=veth"
        )

    def fetch(node, endpoint):
        if endpoint == "/cluster/resources?type=vm":
            if disagrees and node == "Proxmox-2":
                return guests[:-1]
            return guests
        _, _, hostname, kind, vmid, action = endpoint.split("/")
        if action != "config":
            raise ValueError("Unexpected endpoint")
        return configs[(hostname, kind, int(vmid))]

    return fetch


STAGED = {"bc:24:11:aa:00:01", "52:54:00:00:00:02"}


class SnapshotTests(unittest.TestCase):
    def test_running_macs_templates_excluded(self):
        doc, summary = snap.collect(mock_fetch(), STAGED)
        self.assertEqual(summary["cluster_resources"], 4)
        self.assertEqual(summary["configs_checked"], 4)
        self.assertEqual(summary["running_guests"], 3)
        self.assertEqual(summary["templates_excluded"], 1)
        self.assertEqual(summary["unique_guest_macs"], 3)
        self.assertEqual(summary["matches_staged_mac_inventory"], 2)
        self.assertEqual(doc["guests_by_mac"]["bc:24:11:aa:00:01"]["node"],
                         "PROXMOX")
        self.assertNotIn("secret", json.dumps(doc))
        self.assertNotIn("guests_by_mac", summary)

    def test_duplicate_refused(self):
        with self.assertRaisesRegex(ValueError, "Duplicate running guest MAC"):
            snap.collect(mock_fetch(duplicate=True), STAGED)

    def test_nodes_disagree_refused(self):
        with self.assertRaisesRegex(ValueError, "disagree"):
            snap.collect(mock_fetch(disagrees=True), STAGED)

    def test_missing_mac_refused(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            snap.collect(mock_fetch(missing_mac=True), STAGED)

    def test_zero_overlap_refused(self):
        with self.assertRaisesRegex(ValueError, "No MAC overlap"):
            snap.collect(mock_fetch(), {"11:22:33:44:55:66"})

    def test_qemu_lxc_mac_parsing(self):
        self.assertEqual(snap.parse_macs(
            "qemu", {"net0": "virtio=BC:24:11:AA:00:01,bridge=vmbr0"}),
            ["bc:24:11:aa:00:01"])
        self.assertEqual(snap.parse_macs(
            "lxc", {"net0": "hwaddr=52:54:00:00:00:02,type=veth"}),
            ["52:54:00:00:00:02"])

    def test_atomic_file_new_only_no_overwrite(self):
        doc, _ = snap.collect(mock_fetch(), STAGED)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "proxmox-guests.json"
            snap.publish_new(path, doc)
            previous = path.read_bytes()
            self.assertEqual(os.stat(path).st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(previous), doc)
            with self.assertRaises(FileExistsError):
                snap.publish_new(path, {"schema_version": 99})
            self.assertEqual(path.read_bytes(), previous)

    def test_symlink_destination_refused(self):
        doc, _ = snap.collect(mock_fetch(), STAGED)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "proxmox-guests.json"
            target = Path(directory) / "do-not-touch"
            target.write_text("unchanged")
            path.symlink_to(target)
            with self.assertRaises(FileExistsError):
                snap.publish_new(path, doc)
            self.assertEqual(target.read_text(), "unchanged")

    def test_inventory_macs_normalised(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inventory.json"
            path.write_text(json.dumps({
                "192.168.2.1": {"mac": "BC-24-11-AA-00-01"},
                "192.168.2.2": {"mac": "invalid"},
            }))
            self.assertEqual(
                snap.inspect_inventory(path), {"bc:24:11:aa:00:01"},
            )


if __name__ == "__main__":
    unittest.main()
