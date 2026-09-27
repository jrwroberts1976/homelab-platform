"""Offline guards for interrupted Gate 3b transfer recovery."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2] / "ansible/playbooks"
RECOVER = ROOT / "network-host-monitor01-preactivation-recover.yml"


class PreActivationRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code = RECOVER.read_text()
        cls.plays = yaml.safe_load(cls.code)
        cls.target, cls.source = [p["tasks"] for p in cls.plays]

    def test_destination_is_checked_before_source_restarts(self):
        self.assertEqual([p["hosts"] for p in self.plays],
                         ["monitoring_hosts", "Proxmox-2"])
        self.assertTrue(all(p["any_errors_fatal"] for p in self.plays))
        self.assertIn("cutover_pre_activation_recovery_approved",
                      str(self.target[0]))
        self.assertIn("RESTORE_FROZEN_SOURCE_BEFORE_ACTIVATION",
                      str(self.target[0]))
        self.assertIn("recovery_collector_unit",
                      str(self.source[0]))

    def test_partial_transfer_does_not_require_target_alert_files_or_backup(self):
        self.assertNotIn("ansible.builtin.slurp", str(self.target))
        self.assertNotIn("alerted-macs.json", str(self.target))
        self.assertNotIn("final-transfer-", str(self.target))
        self.assertNotIn("ansible.builtin.systemd_service", str(self.target))
        self.assertNotIn("ansible.builtin.copy", str(self.target))
        self.assertNotIn("ansible.builtin.file", str(self.target))

    def test_no_marker_and_unwired_notifier_are_mandatory(self):
        self.assertIn("network-discovery-cutover-approved", str(self.target))
        self.assertIn("not recovery_target_paths.results[0].stat.exists",
                      str(self.target))
        self.assertIn("'ExecStartPost=' not in recovery_collector_unit.stdout",
                      self.code)
        self.assertIn("'EnvironmentFile=' not in recovery_collector_unit.stdout",
                      self.code)
        self.assertIn("recovery_target_notifier.rc == 1", self.code)

    def test_all_five_source_files_and_original_unit_hashes_before_restart(self):
        for name in ("inventory.json", "deep-profiles.json", "enrichment.json",
                     "alerted-macs.json", "alerts.env"):
            self.assertIn(name, self.plays[1]["vars"]["original_files"])
        steps = [t["name"] for t in self.source]
        restart = steps.index("Restore only originally enabled and active source timers")
        for check in (
            "Require exact change identity and complete original timer/data manifest",
            "Reject unreviewed source unit edits or lost rollback files",
            "Refuse lost or modified source registry, recipient or evidence",
            "Reject any partial restart; manual reconciliation required",
            "Fail closed unless target remains fully inert before restoring old owner",
        ):
            self.assertLess(steps.index(check), restart)
        self.assertIn("recovery_manifest.timers[item] == 'enabled'", self.code)
        self.assertIn("recovery_manifest.timer_activity[item] == 'active'",
                      self.code)

    def test_recovery_does_not_destroy_partial_target_state(self):
        self.assertNotIn("state: absent", self.code)
        self.assertNotIn("ansible.builtin.template:", self.code)
        self.assertNotIn("ansible.builtin.copy:", self.code)
        self.assertNotIn("ansible.builtin.file:", self.code)
        self.assertIn("preserve partial target", self.code)


if __name__ == "__main__":
    unittest.main()
