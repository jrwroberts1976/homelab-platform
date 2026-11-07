#!/usr/bin/env python3
"""Offline tests for Suricata logrotate deployment recovery decisions."""

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "playbooks/router-01-suricata-logrotate-deploy.draft.yml"

ORIGINAL = (
    "f95789a4166f06c69695c31de79bf586"
    "cd72c0a862cf50292e35d2ae342f6c96"
)
CANDIDATE = (
    "19f06bf2b87db4307d11e5e6be7922e8"
    "03acc63fcbc3d7c357bc39e975ede677"
)


def recovery_decision(active, backup):
    """Model the intended recovery policy, not Ansible execution."""
    if active not in (ORIGINAL, CANDIDATE):
        return "REFUSE"
    if backup != ORIGINAL:
        return "REFUSE"
    if active == ORIGINAL:
        return "PRESERVE"
    return "RESTORE"


class SuricataRecoveryTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.play = yaml.safe_load(DRAFT.read_text())[0]
        cls.stage = next(
            task for task in cls.play["tasks"]
            if task["name"] ==
            "Stage and validate candidate with guaranteed cleanup"
        )

    def test_development_lock(self):
        self.assertEqual(
            self.play["pre_tasks"][0]["name"],
            "DEVELOPMENT LOCK - never execute draft",
        )
        self.assertIn(
            "ansible.builtin.fail",
            self.play["pre_tasks"][0],
        )

    def test_original_preserved(self):
        self.assertEqual(
            recovery_decision(ORIGINAL, ORIGINAL),
            "PRESERVE",
        )

    def test_candidate_restored(self):
        self.assertEqual(
            recovery_decision(CANDIDATE, ORIGINAL),
            "RESTORE",
        )

    def test_unknown_active_refused(self):
        self.assertEqual(
            recovery_decision("0" * 64, ORIGINAL),
            "REFUSE",
        )

    def test_missing_active_refused(self):
        self.assertEqual(
            recovery_decision(None, ORIGINAL),
            "REFUSE",
        )

    def test_invalid_backup_refused(self):
        self.assertEqual(
            recovery_decision(CANDIDATE, "0" * 64),
            "REFUSE",
        )

    def test_rescue_and_cleanup_present(self):
        self.assertIn("rescue", self.stage)
        self.assertIn("always", self.stage)

    def test_restore_is_conditioned_on_candidate_hash(self):
        restore = next(
            task for task in self.stage["rescue"]
            if task["name"] ==
            "Restore original only if active policy is approved candidate"
        )
        self.assertIn(
            "router_suricata_logrotate_candidate_sha256",
            restore["when"],
        )


if __name__ == "__main__":
    unittest.main()
