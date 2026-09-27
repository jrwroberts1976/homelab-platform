"""Offline checks: Gate 3b freeze is approval-gated and source-only.

These structural tests never connect to hosts, stop services or read secrets.
"""
from pathlib import Path
import unittest
import yaml

PATH = (Path(__file__).resolve().parents[2] /
        "ansible/playbooks/network-host-monitor01-source-freeze.yml")


class SourceFreezeGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = PATH.read_text()
        cls.plays = yaml.safe_load(cls.raw)
        cls.steps = cls.plays[1]["tasks"]

    def test_reuses_read_only_two_host_gate_and_only_freezes_source(self):
        self.assertEqual(self.plays[0]["import_playbook"],
                         "network-host-monitor01-cutover-preflight.yml")
        self.assertEqual(len(self.plays), 2)
        self.assertEqual(self.plays[1]["hosts"], "Proxmox-2")
        self.assertTrue(self.plays[1]["any_errors_fatal"])
        self.assertEqual(self.plays[1]["become"], True)

    def test_explicit_approval_precedes_every_mutation(self):
        first = self.steps[0]
        self.assertIn("ansible.builtin.assert", first)
        conditions = str(first["ansible.builtin.assert"]["that"])
        for guard in ("cutover_source_stop_approved", "cutover_approval_phrase",
                      "cutover_change_id", "target_guest_counts",
                      "target_template_check"):
            self.assertIn(guard, conditions)
        mutations = ("ansible.builtin.file", "ansible.builtin.copy",
                     "ansible.builtin.systemd_service")
        first_mutation = next(i for i, t in enumerate(self.steps)
                              if any(m in t for m in mutations))
        self.assertGreater(first_mutation, 0)
        self.assertTrue(any("delegate_to" in t and
                            t["delegate_to"] == "monitor-01"
                            for t in self.steps[:first_mutation]))

    def test_mutations_remain_on_source_and_only_discovery_timers_stop(self):
        for task in self.steps:
            module = task.get("ansible.builtin.systemd_service")
            if module:
                self.assertEqual(module["state"], "stopped")
                self.assertIs(module["enabled"], False)
                self.assertEqual(module["name"], "{{ item }}")
                self.assertEqual(task["loop"], "{{ source_timers }}")
            if task.get("delegate_to"):
                self.assertEqual(task["delegate_to"], "monitor-01")
                self.assertEqual(set(task.keys()) & {
                    "ansible.builtin.copy", "ansible.builtin.file",
                    "ansible.builtin.systemd_service"}, set())
        self.assertNotIn("ansible.builtin.import_role", self.raw)
        for forbidden in ("state: started", "enabled: true",
                          "network-discovery-cutover-approved\n        state: touch",
                          "nmap -", "sendmail"):
            self.assertNotIn(forbidden, self.raw)

    def test_root_only_rollback_metadata_precedes_stop(self):
        labels = [t["name"] for t in self.steps]
        stop = next(i for i, t in enumerate(self.steps)
                    if "Disable and stop ONLY" in t["name"])
        for label in ("Preserve exact installed network systemd units",
                      "Save rollback timer states",
                      "Require protected rollback evidence"):
            self.assertTrue(any(label in name for name in labels[:stop]))
        self.assertIn("source_freeze_dir", self.raw)
        self.assertIn("mode: '0700'", self.raw)
        self.assertIn("mode: '0600'", self.raw)
        self.assertIn("alerted-macs.json", self.raw)
        self.assertIn("alerts.env", self.raw)

    def test_drain_and_hash_before_explicit_transfer_hold(self):
        labels = [t["name"] for t in self.steps]
        stop = next(i for i, name in enumerate(labels)
                    if "Disable and stop ONLY" in name)
        drain = next(i for i, name in enumerate(labels)
                     if "Wait for any in-flight" in name)
        hashes = next(i for i, name in enumerate(labels)
                      if "Capture final frozen source SHA" in name)
        hold = next(i for i, name in enumerate(labels)
                    if "mandatory hold" in name)
        self.assertTrue(stop < drain < hashes < hold)
        self.assertIn("detached_notifier", self.raw)
        self.assertIn("60", self.raw)
        self.assertIn("frozen-source-sha256.json", self.raw)


if __name__ == "__main__":
    unittest.main()
