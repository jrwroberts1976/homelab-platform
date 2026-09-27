"""Static guardrails for DRAFT, deliberately not-yet-authorised Gate 3 phases."""
from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2] / "ansible/playbooks"
FREEZE = ROOT / "network-host-monitor01-cutover-freeze.yml"
TRANSFER = ROOT / "network-host-monitor01-cutover-transfer.yml"
ROLLBACK = ROOT / "network-host-monitor01-cutover-rollback-before-activation.yml"


class GuardedCutoverPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.freeze = yaml.safe_load(FREEZE.read_text())
        cls.transfer = yaml.safe_load(TRANSFER.read_text())
        cls.rollback = yaml.safe_load(ROLLBACK.read_text())

    def test_freeze_requires_live_two_host_preflight_before_any_mutation(self):
        self.assertEqual(self.freeze[0]["import_playbook"],
                         "network-host-monitor01-cutover-preflight.yml")
        self.assertEqual(self.freeze[1]["hosts"], "monitoring_hosts")
        self.assertEqual(self.freeze[2]["hosts"], "Proxmox-2")
        self.assertIn("destination_free_bytes", str(self.freeze[1]))
        tasks = self.freeze[2]["tasks"]
        self.assertIn("gate3_allow_source_freeze", str(tasks[0]))
        self.assertIn("YES_PAUSE_PROXMOX2_NETWORK_DISCOVERY", str(tasks[0]))
        self.assertIn("gate3_transaction", str(tasks[0]))
        originals = next(
            i for i, task in enumerate(tasks)
            if task.get("name", "").startswith("Preserve exact pre-freeze")
        )
        stop = next(
            i for i, task in enumerate(tasks)
            if task.get("name", "").startswith("Stop and disable")
        )
        self.assertLess(originals, stop)
        self.assertEqual(tasks[stop]["ansible.builtin.systemd_service"]["state"],
                         "stopped")
        self.assertIs(tasks[stop]["ansible.builtin.systemd_service"]["enabled"],
                      False)
        self.assertIn("until", tasks[stop + 1])
        self.assertIn("alerted-macs.json", FREEZE.read_text())
        self.assertIn("alerts.env", FREEZE.read_text())
        self.assertNotIn("state: started", FREEZE.read_text())
        self.assertNotIn("send_message(", FREEZE.read_text())
        self.assertNotIn("nmap ", FREEZE.read_text())

    def test_transfer_rechecks_frozen_source_and_backs_up_target_first(self):
        self.assertEqual([p["hosts"] for p in self.transfer],
                         ["Proxmox-2", "monitoring_hosts"])
        self.assertIn("gate3_allow_final_transfer", str(self.transfer[0]))
        self.assertIn("YES_TRANSFER_FROZEN_NETWORK_STATE", str(self.transfer[0]))
        target = self.transfer[1]["tasks"]
        backup_pos = next(i for i, task in enumerate(target)
                          if task.get("name", "").startswith("Preserve all four"))
        transfer_pos = next(i for i, task in enumerate(target)
                            if task.get("name", "").startswith("Transfer the five"))
        self.assertLess(backup_pos, transfer_pos)
        self.assertEqual(
            target[transfer_pos]["ansible.builtin.copy"]["mode"], "0600"
        )
        self.assertIs(target[transfer_pos]["ansible.builtin.copy"]["force"], True)
        self.assertIs(target[transfer_pos]["no_log"], True)
        self.assertIn("proxmox-guests.json", TRANSFER.read_text())
        self.assertIn("alerted-macs.json", TRANSFER.read_text())
        self.assertIn("source_sha256", TRANSFER.read_text())
        self.assertIn("snapshot_age_seconds", TRANSFER.read_text())
        self.assertNotIn("ansible.builtin.systemd_service", TRANSFER.read_text())
        self.assertNotIn("--test-email", TRANSFER.read_text())

    def test_rollback_verifies_target_inactive_before_restarting_source(self):
        self.assertEqual([p["hosts"] for p in self.rollback],
                         ["monitoring_hosts", "Proxmox-2"])
        target_text = str(self.rollback[0])
        source_text = str(self.rollback[1])
        self.assertIn("not target_cutover_marker.stat.exists", target_text)
        self.assertIn("ExecStartPost=", target_text)
        self.assertIn("EnvironmentFile=", target_text)
        self.assertIn("gate3_allow_preactivation_rollback", source_text)
        self.assertIn("source_sha256", source_text)
        self.assertIn("prior_timer_enabled", source_text)
        self.assertNotIn("ansible.builtin.systemd_service", target_text)
        self.assertEqual(sum("ansible.builtin.systemd_service" in t
                             for t in self.rollback[1]["tasks"]), 1)

    def test_all_phase_credentials_suppressed_and_no_target_approval_marker_created(self):
        for path in (FREEZE, TRANSFER, ROLLBACK):
            content = path.read_text()
            self.assertNotIn("state: touch", content)
            self.assertNotIn("send_message(", content)
            self.assertNotIn("systemctl start homelab-network-host-collector", content)
        self.assertNotIn("network-discovery-cutover-approved", FREEZE.read_text())
        self.assertIn("network-discovery-cutover-approved",
                      TRANSFER.read_text())


if __name__ == "__main__":
    unittest.main()
