"""Offline contract tests: approved-only final transfer and mandatory activation hold."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2] / "ansible/playbooks"
TRANSFER = ROOT / "network-host-monitor01-final-transfer.yml"
FREEZE = ROOT / "network-host-monitor01-source-freeze.yml"


class ProtectedFinalTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = TRANSFER.read_text()
        cls.plays = yaml.safe_load(cls.raw)
        cls.source = cls.plays[0]["tasks"]
        cls.target = cls.plays[1]["tasks"]

    def test_two_distinct_hosts_and_explicit_transfer_approval(self):
        self.assertEqual([p["hosts"] for p in self.plays],
                         ["Proxmox-2", "monitoring_hosts"])
        self.assertTrue(all(p.get("any_errors_fatal") for p in self.plays))
        for tasks in (self.source, self.target):
            guard = str(tasks[0])
            self.assertIn("cutover_final_transfer_approved", guard)
            self.assertIn("COPY_FROZEN_NETWORK_STATE", guard)
            self.assertIn("cutover_change_id", guard)

    def test_never_activates_notifier_or_network_jobs(self):
        self.assertNotIn("ansible.builtin.systemd_service:", self.raw)
        self.assertNotIn("ansible.builtin.import_role:", self.raw)
        self.assertNotIn("state: touch", self.raw)
        self.assertNotIn("enabled: true", self.raw)
        for task in self.source + self.target:
            self.assertNotIn("ansible.builtin.template", task)
            self.assertNotIn("ansible.builtin.script", task)
            if task.get("delegate_to"):
                self.assertNotIn("ansible.builtin.copy", task)
                self.assertNotIn("ansible.builtin.file", task)
        self.assertIn("not final_approval_marker.stat.exists", self.raw)

    def test_preserves_five_original_source_files_and_four_staged_jsons(self):
        first = self.plays[0]["vars"]
        second = self.plays[1]["vars"]
        self.assertEqual(first["source_names"], [
            "inventory.json", "deep-profiles.json", "enrichment.json",
            "alerted-macs.json", "alerts.env"])
        self.assertEqual(second["copied_names"], first["source_names"])
        self.assertEqual(second["target_existing"], [
            "inventory.json", "deep-profiles.json", "enrichment.json",
            "proxmox-guests.json"])
        self.assertIn("force: false", self.raw)
        self.assertIn("mode: '0700'", self.raw)
        self.assertIn("mode: '0600'", self.raw)
        self.assertIn("freeze_sha", self.raw)

    def test_requires_source_drain_before_snapshot_then_target_backup_before_copy(self):
        snames = [t["name"] for t in self.source]
        tnames = [t["name"] for t in self.target]
        drain = snames.index("Refuse incomplete or interrupted freeze")
        snapshot = snames.index(
            "Create private immutable-name final source snapshot directory")
        self.assertLess(drain, snapshot)
        backup = tnames.index(
            "Back up all four prior protected JSON files before replacing any of them")
        copy = tnames.index(
            "Transfer three source datasets, full historic first-seen registry and recipient environment")
        self.assertLess(backup, copy)
        self.assertIn("unmatched_guest_macs", self.raw)
        self.assertIn("snapshot_age_seconds", self.raw)
        self.assertIn("cutover marker", self.raw.lower())

    def test_source_freeze_creates_protected_parent_before_subdirectory(self):
        freeze = yaml.safe_load(FREEZE.read_text())[1]["tasks"]
        labels = [t["name"] for t in freeze]
        self.assertLess(
            labels.index("Create private source-only freeze directory with explicit parent permissions"),
            labels.index("Create private rollback unit directory"))


if __name__ == "__main__":
    unittest.main()
