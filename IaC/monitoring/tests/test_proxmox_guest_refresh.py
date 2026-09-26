"""Offline atomic-refresh transaction tests: no Proxmox API or Nmap required."""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import unittest

FILE_DIR = (
    Path(__file__).resolve().parents[2]
    / "ansible/roles/network_host_enrichment/files"
)
spec = importlib.util.spec_from_file_location(
    "guest_refresh", FILE_DIR / "proxmox-guest-mac-refresh.py"
)
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)
refresh.READER_DIR = str(FILE_DIR)


def guest(mac, vmid, name):
    return {
        "source": "proxmox_cluster_api",
        "node": "PROXMOX" if vmid % 2 == 0 else "Proxmox-2",
        "guest_type": "qemu" if vmid % 2 == 0 else "lxc",
        "vmid": str(vmid),
        "name": name,
    }


def document(now, records):
    return {
        "schema_version": 1,
        "source": "proxmox_cluster_api",
        "generated_at": now,
        "cluster_resources": len(records) + 2,
        "templates_excluded": 2,
        "guests_by_mac": records,
    }


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.addCleanup(self.root.cleanup)
        root = Path(self.root.name)
        self.path = root / "proxmox-guests.json"
        self.backups = root / "backups"
        self.backups.mkdir(mode=0o700)
        self.now = int(time.time())
        self.inventory = {
            "192.168.2.21": {"mac": "52:54:00:00:00:01"},
            "192.168.2.22": {"mac": "52:54:00:00:00:02"},
            "192.168.2.23": {"mac": "52:54:00:00:00:03"},
            "192.168.2.24": {"mac": "52:54:00:00:00:04"},
        }
        self.old = document(self.now - 3600, {
            f"52:54:00:00:00:{i:02x}": guest(
                f"52:54:00:00:00:{i:02x}", 200 + i, f"host-{i}"
            ) for i in range(1, 5)
        })
        self.old_raw = json.dumps(self.old, sort_keys=True).encode()
        self.path.write_bytes(self.old_raw)
        self.path.chmod(0o600)

    def updated(self, **kwargs):
        current = json.loads(self.path.read_text())
        current["generated_at"] = self.now
        current["guests_by_mac"]["52:54:00:00:00:01"]["node"] = "Proxmox-2"
        current.update(kwargs)
        return current

    def run_refresh(self, candidate):
        return refresh.refresh(
            self.path, self.inventory, self.backups, candidate,
            now=self.now, owner_uid=os.getuid(),
        )

    def test_preserves_original_backup_and_atomically_replaces(self):
        changed = self.updated()
        result = self.run_refresh(changed)
        self.assertTrue(result["backup_verified"])
        self.assertEqual(result["refreshed_guest_macs"], 4)
        self.assertEqual(result["matched_lan_macs"], 4)
        self.assertEqual(json.loads(self.path.read_text()), changed)
        self.assertEqual(os.stat(self.path).st_mode & 0o777, 0o600)
        digest = hashlib.sha256(self.old_raw).hexdigest()
        old_backup = self.backups / f"proxmox-guests.{digest}.json"
        self.assertEqual(old_backup.read_bytes(), self.old_raw)
        self.assertEqual(os.stat(old_backup).st_mode & 0o777, 0o600)

    def test_missing_overlap_fails_without_mutating_original(self):
        bad = self.updated()
        bad["guests_by_mac"] = {
            "aa:bb:cc:00:00:01": guest("aa:bb:cc:00:00:01", 201, "different")
        }
        with self.assertRaisesRegex(ValueError, "overlap"):
            self.run_refresh(bad)
        self.assertEqual(self.path.read_bytes(), self.old_raw)
        self.assertEqual(list(self.backups.glob("*.json")), [])

    def test_large_visibility_drop_fails_without_backup(self):
        bad = self.updated()
        bad["guests_by_mac"] = dict(
            list(bad["guests_by_mac"].items())[:2]
        )
        with self.assertRaisesRegex(ValueError, "visibility drop"):
            self.run_refresh(bad)
        self.assertEqual(self.path.read_bytes(), self.old_raw)

    def test_invalid_candidate_provenance_fails_closed(self):
        bad = self.updated(source="unknown")
        with self.assertRaisesRegex(ValueError, "provenance"):
            self.run_refresh(bad)
        self.assertEqual(self.path.read_bytes(), self.old_raw)

    def test_symlink_snapshot_refused(self):
        target = self.path.parent / "do-not-touch"
        target.write_bytes(self.old_raw)
        target.chmod(0o600)
        self.path.unlink()
        self.path.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "metadata"):
            self.run_refresh(self.updated())
        self.assertEqual(target.read_bytes(), self.old_raw)

    def test_insecure_backup_directory_refused(self):
        self.backups.chmod(0o755)
        with self.assertRaisesRegex(ValueError, "directory is unsafe"):
            self.run_refresh(self.updated())
        self.assertEqual(self.path.read_bytes(), self.old_raw)

    def test_existing_backup_hash_conflict_blocks_refresh(self):
        digest = hashlib.sha256(self.old_raw).hexdigest()
        old_backup = self.backups / f"proxmox-guests.{digest}.json"
        old_backup.write_bytes(b"wrong contents")
        old_backup.chmod(0o600)
        with self.assertRaisesRegex(ValueError, "Conflicting snapshot backup"):
            self.run_refresh(self.updated())
        self.assertEqual(self.path.read_bytes(), self.old_raw)
        self.assertEqual(old_backup.read_bytes(), b"wrong contents")

    def test_old_snapshot_can_be_older_than_enricher_ttl(self):
        old = json.loads(self.path.read_text())
        old["generated_at"] = self.now - 7 * 86400
        self.path.write_text(json.dumps(old))
        self.path.chmod(0o600)
        result = self.run_refresh(self.updated())
        self.assertGreater(result["previous_snapshot_age_seconds"], 48 * 3600)


if __name__ == "__main__":
    unittest.main()
