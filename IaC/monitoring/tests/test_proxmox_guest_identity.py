"""Offline tests for fail-closed MAC association in the staged enricher."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time
import unittest

SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "ansible/roles/network_host_enrichment/files/proxmox_guest_identity.py"
)
spec = importlib.util.spec_from_file_location("guest_identity", SCRIPT)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def snapshot(now, **changes):
    document = {
        "schema_version": 1,
        "source": "proxmox_cluster_api",
        "generated_at": now - 60,
        "cluster_resources": 13,
        "templates_excluded": 2,
        "guests_by_mac": {
            "bc:24:11:aa:00:01": {
                "source": "proxmox_cluster_api",
                "node": "PROXMOX",
                "guest_type": "qemu",
                "vmid": "200",
                "name": "cloud-01",
            },
            "52:54:00:00:00:02": {
                "source": "proxmox_cluster_api",
                "node": "Proxmox-2",
                "guest_type": "lxc",
                "vmid": "101",
                "name": "dns-01",
            },
        },
    }
    document.update(changes)
    return document


LAN = {
    "192.168.2.10": {"mac": "BC-24-11-AA-00-01"},
    "192.168.2.11": {"mac": "52:54:00:00:00:02"},
    "192.168.2.12": {"mac": "invalid"},
}


class GuestIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "proxmox-guests.json"
        self.now = int(time.time())
        self.write(snapshot(self.now))

    def write(self, data, mode=0o600):
        self.path.write_text(json.dumps(data), encoding="utf-8")
        self.path.chmod(mode)

    def read(self, **kwargs):
        return reader.load_snapshot(
            self.path, LAN, now=self.now, owner_uid=os.getuid(), **kwargs
        )

    def test_exact_match_returns_minimal_metadata_not_mac_log(self):
        identities, counts = self.read()
        self.assertEqual(counts["snapshot_guest_macs"], 2)
        self.assertEqual(counts["matched_guest_macs"], 2)
        self.assertEqual(counts["unmatched_guest_macs"], 0)
        self.assertEqual(counts["saved_lan_devices"], 3)
        self.assertEqual(identities["bc:24:11:aa:00:01"]["vmid"], "200")
        self.assertNotIn("bc:24", json.dumps(counts))

    def test_stale_snapshot_refused(self):
        self.write(snapshot(self.now, generated_at=self.now - 172801))
        with self.assertRaisesRegex(ValueError, "stale"):
            self.read()

    def test_future_snapshot_refused(self):
        self.write(snapshot(self.now, generated_at=self.now + 301))
        with self.assertRaisesRegex(ValueError, "timestamp"):
            self.read()

    def test_insecure_mode_refused(self):
        self.path.chmod(0o644)
        with self.assertRaisesRegex(ValueError, "0600"):
            self.read()

    def test_symlink_refused(self):
        target = Path(self.tmp.name) / "original"
        target.write_bytes(self.path.read_bytes())
        target.chmod(0o600)
        self.path.unlink()
        self.path.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "ordinary file"):
            self.read()

    def test_invalid_provenance_refused(self):
        self.write(snapshot(self.now, source="unknown"))
        with self.assertRaisesRegex(ValueError, "provenance"):
            self.read()

    def test_ambiguous_case_mac_refused(self):
        doc = snapshot(self.now)
        doc["guests_by_mac"]["BC:24:11:AA:00:01"] = doc[
            "guests_by_mac"]["bc:24:11:aa:00:01"]
        self.write(doc)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self.read()

    def test_unknown_node_refused(self):
        doc = snapshot(self.now)
        doc["guests_by_mac"]["bc:24:11:aa:00:01"]["node"] = "unexpected"
        self.write(doc)
        with self.assertRaisesRegex(ValueError, "identity"):
            self.read()

    def test_no_lan_overlap_refused(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            reader.load_snapshot(
                self.path, {"a": {"mac": "aa:aa:aa:aa:aa:aa"}},
                owner_uid=os.getuid(), now=self.now,
            )

    def test_one_unmatched_is_reported(self):
        partial = {"192.168.2.10": LAN["192.168.2.10"]}
        _, counts = reader.load_snapshot(
            self.path, partial, owner_uid=os.getuid(), now=self.now,
        )
        self.assertEqual(counts["matched_guest_macs"], 1)
        self.assertEqual(counts["unmatched_guest_macs"], 1)


if __name__ == "__main__":
    unittest.main()
