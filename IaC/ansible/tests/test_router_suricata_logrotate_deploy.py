#!/usr/bin/env python3
"""Offline checks for Suricata logrotate deployment safeguards."""

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK = ROOT / "playbooks/router-01-suricata-logrotate-deploy.yml"


class SuricataLogrotateDeployTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.play = yaml.safe_load(
            PLAYBOOK.read_text(encoding="utf-8")
        )[0]

    def test_exact_target(self):
        self.assertEqual(self.play["hosts"], "router-01")
        self.assertFalse(self.play["gather_facts"])

    def test_approval_disabled_by_default(self):
        self.assertIs(
            self.play["vars"]["router_suricata_logrotate_approved"],
            False,
        )

    def test_approval_gate_exists(self):
        checks = self.play["pre_tasks"][0]["ansible.builtin.assert"]["that"]
        self.assertIn(
            "router_suricata_logrotate_approved | bool",
            checks,
        )
        self.assertIn("not ansible_check_mode", checks)
        self.assertIn("inventory_hostname == 'router-01'", checks)
        self.assertIn("ansible_host == '192.168.2.1'", checks)

    def test_runtime_hostname_verification(self):
        content = str(self.play["pre_tasks"])
        self.assertIn("raspberrypi", content)

    def test_nfq_health_check(self):
        content = str(self.play["pre_tasks"])
        self.assertIn("router-suricata-nfq.service", content)

    def test_no_service_modifications(self):
        content = PLAYBOOK.read_text(encoding="utf-8")
        self.assertNotIn("ansible.builtin.systemd_service:", content)
        self.assertNotIn("state: restarted", content)
        self.assertNotIn("logrotate -f", content)


    def test_baseline_sha256(self):
        expected = (
            "f95789a4166f06c69695c31de79bf586"
            "cd72c0a862cf50292e35d2ae342f6c96"
        )
        self.assertEqual(
            self.play["vars"][
                "router_suricata_logrotate_expected_sha256"
            ],
            expected,
        )

    def test_baseline_stat_uses_sha256(self):
        tasks = self.play["pre_tasks"]
        matches = [
            task["ansible.builtin.stat"]
            for task in tasks
            if task.get("name")
            == "Inspect existing logrotate configuration"
        ]
        self.assertEqual(len(matches), 1)
        self.assertEqual(
            matches[0]["checksum_algorithm"], "sha256"
        )
        self.assertTrue(matches[0]["get_checksum"])
        self.assertFalse(matches[0]["follow"])

    def test_baseline_checks_ownership_and_mode(self):
        checks = str(self.play["pre_tasks"])
        for required in (
            "router_suricata_existing_policy.stat.exists",
            "router_suricata_existing_policy.stat.isreg",
            "router_suricata_existing_policy.stat.pw_name",
            "router_suricata_existing_policy.stat.gr_name",
            "router_suricata_existing_policy.stat.mode",
            "router_suricata_existing_policy.stat.checksum",
        ):
            self.assertIn(required, checks)


    def test_protected_backup_directory(self):
        tasks = self.play["tasks"]
        matches = [
            task["ansible.builtin.file"]
            for task in tasks
            if task.get("name") == "Create protected backup directory"
        ]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["mode"], "0700")
        self.assertEqual(matches[0]["owner"], "root")

    def test_backup_does_not_overwrite_existing_file(self):
        tasks = self.play["tasks"]
        matches = [
            task["ansible.builtin.copy"]
            for task in tasks
            if task.get("name")
            == "Back up original Suricata logrotate policy"
        ]
        self.assertEqual(len(matches), 1)
        self.assertTrue(matches[0]["remote_src"])
        self.assertFalse(matches[0]["force"])
        self.assertEqual(matches[0]["mode"], "0600")

    def test_backup_checksum_verification(self):
        content = str(self.play["tasks"])
        self.assertIn(
            "router_suricata_logrotate_backup_stat.stat.checksum",
            content,
        )
        self.assertIn(
            "router_suricata_logrotate_expected_sha256",
            content,
        )


    def test_candidate_integrity_gate(self):
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

        tasks = self.play["pre_tasks"]

        candidate = [
            task
            for task in tasks
            if task.get("name")
            == "Inspect candidate policy on controller"
        ]
        self.assertEqual(len(candidate), 1)

        stat = candidate[0]["ansible.builtin.stat"]
        self.assertEqual(stat["checksum_algorithm"], "sha256")
        self.assertTrue(stat["get_checksum"])
        self.assertEqual(candidate[0]["delegate_to"], "localhost")
        self.assertFalse(candidate[0]["become"])

        checks = [
            task["ansible.builtin.assert"]["that"]
            for task in tasks
            if task.get("name")
            == "Verify candidate policy checksum on controller"
        ]
        self.assertEqual(len(checks), 1)

        self.assertIn(
            "router_suricata_candidate_stat.stat.checksum == router_suricata_logrotate_candidate_sha256",
            checks[0],
        )


    def test_staging_cleanup_and_installation_block(self):
        tasks = self.play["tasks"]

        staging = [
            task for task in tasks
            if task.get("name")
            == "Stage and validate candidate with guaranteed cleanup"
        ]

        self.assertEqual(len(staging), 1)

        stage = staging[0]

        self.assertIn("block", stage)
        self.assertIn("always", stage)

        cleanup = stage["always"]
        self.assertEqual(len(cleanup), 1)
        self.assertEqual(
            cleanup[0]["name"],
            "Remove temporary candidate staging directory",
        )
        self.assertEqual(
            cleanup[0]["ansible.builtin.file"]["state"],
            "absent",
        )

        self.assertEqual(
            tasks[-1]["name"],
            "Stop before deployment implementation",
        )
        self.assertIn("ansible.builtin.fail", tasks[-1])

    def test_incomplete_deployment_stays_blocked(self):
        tasks = self.play["tasks"]
        self.assertGreaterEqual(len(tasks), 1)
        self.assertEqual(
            tasks[-1]["name"],
            "Stop before deployment implementation",
        )
        self.assertIn("ansible.builtin.fail", tasks[-1])
        self.assertFalse(
            any("ansible.builtin.copy" in task and
                task.get("name", "").startswith("Install")
                for task in tasks)
        )


if __name__ == "__main__":
    unittest.main()
