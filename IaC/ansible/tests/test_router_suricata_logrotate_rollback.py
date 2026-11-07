#!/usr/bin/env python3
"""Offline safety tests for Suricata logrotate rollback."""

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK = ROOT / "playbooks/router-01-suricata-logrotate-rollback.yml"

ORIGINAL_SHA256 = (
    "f95789a4166f06c69695c31de79bf586"
    "cd72c0a862cf50292e35d2ae342f6c96"
)


class SuricataLogrotateRollbackTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.play = yaml.safe_load(
            PLAYBOOK.read_text(encoding="utf-8")
        )[0]

    def test_exact_router_target(self):
        self.assertEqual(self.play["hosts"], "router-01")
        self.assertFalse(self.play["gather_facts"])

    def test_approval_disabled_by_default(self):
        self.assertIs(
            self.play["vars"][
                "router_suricata_logrotate_rollback_approved"
            ],
            False,
        )

    def test_approval_gate(self):
        checks = self.play["pre_tasks"][0][
            "ansible.builtin.assert"
        ]["that"]

        for required in (
            "not ansible_check_mode",
            "router_suricata_logrotate_rollback_approved | bool",
            "inventory_hostname == 'router-01'",
            "ansible_host == '192.168.2.1'",
        ):
            self.assertIn(required, checks)

    def test_original_sha256(self):
        self.assertEqual(
            self.play["vars"][
                "router_suricata_logrotate_original_sha256"
            ],
            ORIGINAL_SHA256,
        )

    def test_backup_integrity_checks(self):
        content = str(self.play["pre_tasks"])

        for required in (
            "checksum_algorithm",
            "sha256",
            "router_suricata_rollback_backup.stat.checksum",
            "router_suricata_logrotate_original_sha256",
            "router_suricata_rollback_backup.stat.mode",
            "router_suricata_rollback_backup.stat.pw_name",
        ):
            self.assertIn(required, content)

    def test_runtime_hostname_check(self):
        self.assertIn("raspberrypi", str(self.play["pre_tasks"]))

    def test_no_service_restart_or_signal(self):
        content = PLAYBOOK.read_text(encoding="utf-8")

        for forbidden in (
            "ansible.builtin.systemd_service:",
            "state: restarted",
            "logrotate -f",
            "kill -HUP",
        ):
            self.assertNotIn(forbidden, content)


    def test_candidate_sha256(self):
        expected = (
            "19f06bf2b87db4307d11e5e6be7922e8"
            "03acc63fcbc3d7c357bc39e975ede677"
        )
        self.assertEqual(
            self.play["vars"][
                "router_suricata_logrotate_candidate_sha256"
            ],
            expected,
        )

    def test_active_policy_uses_sha256(self):
        matches = [
            task["ansible.builtin.stat"]
            for task in self.play["pre_tasks"]
            if task.get("name")
            == "Inspect active policy before rollback"
        ]
        self.assertEqual(len(matches), 1)
        self.assertEqual(
            matches[0]["checksum_algorithm"], "sha256"
        )
        self.assertTrue(matches[0]["get_checksum"])
        self.assertFalse(matches[0]["follow"])

    def test_active_policy_identity_required(self):
        matches = [
            task["ansible.builtin.assert"]["that"]
            for task in self.play["pre_tasks"]
            if task.get("name")
            == "Refuse rollback of an unexpected active policy"
        ]
        self.assertEqual(len(matches), 1)
        checks = matches[0]

        for required in (
            "router_suricata_rollback_active.stat.exists",
            "router_suricata_rollback_active.stat.isreg",
            "router_suricata_rollback_active.stat.pw_name == 'root'",
            "router_suricata_rollback_active.stat.gr_name == 'root'",
            "router_suricata_rollback_active.stat.mode == '0644'",
            "router_suricata_rollback_active.stat.checksum == router_suricata_logrotate_candidate_sha256",
        ):
            self.assertIn(required, checks)


    def test_restore_requires_approval_gate(self):
        checks = self.play["pre_tasks"][0][
            "ansible.builtin.assert"
        ]["that"]
        self.assertIn(
            "router_suricata_logrotate_rollback_approved | bool",
            checks,
        )

    def test_restoration_sequence(self):
        tasks = self.play["tasks"]
        names = [task["name"] for task in tasks]

        expected = [
            "Validate protected original policy in debug mode",
            "Capture NFQUEUE PID before restoration",
            "Require running NFQUEUE process before restoration",
            "Recheck active policy immediately before restoration",
            "Refuse restoration if active policy has changed",
            "Restore exact verified original configuration",
            "Verify restored configuration SHA-256",
            "Require exact original configuration",
            "Capture NFQUEUE PID after restoration",
            "Require unchanged NFQUEUE process",
            "Confirm Suricata NFQUEUE remains active",
        ]

        self.assertEqual(names, expected)

    def test_restore_source_and_destination(self):
        tasks = self.play["tasks"]
        restore = next(
            task["ansible.builtin.copy"]
            for task in tasks
            if task["name"]
            == "Restore exact verified original configuration"
        )

        self.assertTrue(restore["remote_src"])
        self.assertEqual(restore["mode"], "0644")
        self.assertEqual(restore["owner"], "root")
        self.assertEqual(restore["group"], "root")
        self.assertTrue(restore["backup"])

    def test_final_restore_checksum_gate(self):
        content = str(self.play["tasks"])
        self.assertIn(
            "router_suricata_rollback_final_stat.stat.checksum",
            content,
        )
        self.assertIn(
            "router_suricata_logrotate_candidate_sha256",
            content,
        )
        self.assertIn(
            "router_suricata_rollback_restored_stat.stat.checksum",
            content,
        )
        self.assertIn(
            "router_suricata_logrotate_original_sha256",
            content,
        )


if __name__ == "__main__":
    unittest.main()
