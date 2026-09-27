"""Offline nonproduction checks of independent Gate 3 activation and rollback."""
from pathlib import Path
import unittest
import yaml

PLAYBOOKS = Path(__file__).resolve().parents[2] / "ansible/playbooks"


class GuardedActivationRollbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.act = yaml.safe_load(
            (PLAYBOOKS / "network-host-monitor01-activate.yml").read_text())
        cls.rollback = yaml.safe_load(
            (PLAYBOOKS / "network-host-monitor01-rollback.yml").read_text())
        cls.act_text = str(cls.act)
        cls.rollback_text = str(cls.rollback)

    def test_activation_requires_separate_approval_and_both_hosts(self):
        self.assertEqual([p["hosts"] for p in self.act],
                         ["Proxmox-2", "monitoring_hosts"])
        self.assertTrue(all(p["any_errors_fatal"] for p in self.act))
        for play in self.act:
            approval = str(play["tasks"][0])
            self.assertIn("cutover_activate_approved", approval)
            self.assertIn("ACTIVATE_MONITOR01_DISCOVERY", approval)
            self.assertIn("cutover_change_id", approval)

    def test_activation_source_is_strictly_read_only(self):
        for task in self.act[0]["tasks"]:
            self.assertFalse(set(task) & {
                "ansible.builtin.systemd_service", "ansible.builtin.file",
                "ansible.builtin.copy", "ansible.builtin.template"})
        self.assertIn("final-transfer", self.act_text)
        self.assertIn("activation_frozen_sha", self.act_text)

    def test_activation_requires_full_five_file_parity_before_first_mutation(self):
        tasks = self.act[1]["tasks"]
        names = [t["name"] for t in tasks]
        verify = names.index(
            "Require final transfer exactly matches freeze, including complete notification history")
        first_mutation = next(i for i, t in enumerate(tasks)
                              if set(t) & {"ansible.builtin.copy",
                                          "ansible.builtin.file",
                                          "ansible.builtin.systemd_service"}
                              or ("ansible.builtin.template" in t
                                  and not t.get("check_mode")))
        self.assertLess(verify, first_mutation)
        self.assertIn("approved_notifier_compare.changed", self.act_text)
        self.assertIn("snapshot_age_seconds", self.act_text)
        self.assertIn("unmatched_guest_macs", self.act_text)

    def test_activation_starts_only_target_and_never_enables_deep_scans(self):
        tasks = self.act[1]["tasks"]
        mutations = [t for t in tasks if "ansible.builtin.systemd_service" in t]
        self.assertTrue(mutations)
        for t in tasks:
            if t.get("delegate_to") == "Proxmox-2":
                self.assertFalse(set(t) & {
                    "ansible.builtin.systemd_service", "ansible.builtin.copy",
                    "ansible.builtin.file", "ansible.builtin.template"})
        enabled = [str(t) for t in mutations if
                   t["ansible.builtin.systemd_service"].get("enabled") is True]
        self.assertEqual(len(enabled), 1)
        self.assertNotIn("homelab-network-host-deep-profiler.timer", enabled[0])
        self.assertIn("rollback", self.act_text.lower())

    def test_rollback_stops_target_before_any_source_restart(self):
        self.assertEqual([p["hosts"] for p in self.rollback],
                         ["Proxmox-2", "monitoring_hosts", "Proxmox-2"])
        self.assertTrue(all(p["any_errors_fatal"] for p in self.rollback))
        for tasks in (self.rollback[0]["tasks"], self.rollback[1]["tasks"]):
            self.assertIn("cutover_rollback_approved", str(tasks[0]))
        self.assertIn("ROLLBACK_MONITOR01_TO_PROXMOX2", self.rollback_text)
        self.assertNotIn("ansible.builtin.systemd_service", str(self.rollback[0]))
        self.assertIn("previous_source.timer_activity", self.rollback_text)
        self.assertIn("rollback_target_registry.stat.checksum", self.rollback_text)

    def test_rollback_rejects_new_alert_history_before_resuming_source(self):
        target = self.rollback[1]["tasks"]
        source = self.rollback[2]["tasks"]
        assert_index = next(i for i,t in enumerate(target)
                            if "Refuse source notifier restart" in t["name"])
        marker_index = next(i for i,t in enumerate(target)
                            if "Remove target enrichment approval" in t["name"])
        self.assertLess(assert_index, marker_index)
        self.assertTrue(any("ansible.builtin.systemd_service" in t
                            for t in source))
        self.assertIn("previous_source_sha", self.rollback_text)
        self.assertIn("state: absent", (PLAYBOOKS /
                      "network-host-monitor01-rollback.yml").read_text())


if __name__ == "__main__":
    unittest.main()
