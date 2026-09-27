"""Gate 3a remains a read-only planning check with no cutover side effects."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2] / "ansible"
PREFLIGHT = ROOT / "playbooks/network-host-monitor01-cutover-preflight.yml"


class ReadOnlyGate3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code = PREFLIGHT.read_text()
        cls.plays = yaml.safe_load(cls.code)

    def test_expected_source_then_target_and_no_tasks_mutate_hosts(self):
        self.assertEqual(
            [play["hosts"] for play in self.plays],
            ["Proxmox-2", "monitoring_hosts"],
        )
        prohibited = {
            "ansible.builtin.copy",
            "ansible.builtin.file",
            "ansible.builtin.apt",
            "ansible.builtin.script",
            "ansible.builtin.systemd_service",
            "ansible.builtin.import_role",
            "ansible.builtin.fetch",
            "ansible.builtin.reboot",
        }
        for play in self.plays:
            for task in play["tasks"]:
                self.assertFalse(prohibited & task.keys(), task.get("name"))

    def test_only_template_task_is_explicitly_check_mode_no_diff_and_no_log(self):
        template_tasks = [
            task for play in self.plays for task in play["tasks"]
            if "ansible.builtin.template" in task
        ]
        self.assertEqual(len(template_tasks), 1)
        task = template_tasks[0]
        self.assertIs(task["check_mode"], True)
        self.assertIs(task["diff"], False)
        self.assertIs(task["no_log"], True)

    def test_all_shell_tasks_are_read_only_and_logs_suppressed(self):
        for play in self.plays:
            for task in play["tasks"]:
                if "ansible.builtin.shell" in task:
                    self.assertTrue(task.get("no_log"), task.get("name"))
                    shell = str(task["ansible.builtin.shell"])
                    self.assertNotIn("--refresh", shell)
                    self.assertNotIn("--test-email", shell)
                    self.assertNotIn("send_message(", shell)
                    self.assertNotIn("systemctl stop", shell)
                    self.assertNotIn("systemctl start", shell)
                    self.assertNotIn("nmap ", shell)
        self.assertIn("--check", self.code)
        self.assertNotIn("systemctl disable", self.code)
        self.assertNotIn("network-discovery-cutover-approved\n", self.code)

    def test_preserves_legacy_host_and_all_protected_files(self):
        for path in (
            "inventory.json", "deep-profiles.json", "enrichment.json",
            "alerted-macs.json", "alerts.env", "proxmox-guests.json",
        ):
            self.assertIn(path, self.code)
        for timer in (
            "homelab-network-host-collector.timer",
            "homelab-network-host-enricher.timer",
            "homelab-network-host-deep-profiler.timer",
            "homelab-network-os-evidence.timer",
            "homelab-proxmox-guest-refresh.timer",
        ):
            self.assertIn(timer, self.code)
        self.assertIn("pending", self.code)
        self.assertIn("snapshot_age_seconds", self.code)
        self.assertIn("ConditionPathExists=", self.code)


if __name__ == "__main__":
    unittest.main()
