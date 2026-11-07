#!/usr/bin/env python3
"""Offline guardrails for the candidate Suricata rotation policy."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "files/router-suricata.logrotate"


class SuricataLogrotatePolicyTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.text = POLICY.read_text(encoding="utf-8")

        # Ignore comments and blank lines.
        cls.lines = [
            line.strip()
            for line in cls.text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]

    def test_expected_log_patterns(self):
        self.assertIn("/var/log/suricata/*.log", self.lines)
        self.assertIn("/var/log/suricata/*.json", self.lines)

    def test_rotation_frequency(self):
        self.assertIn("daily", self.lines)
        self.assertIn("maxsize 100M", self.lines)

    def test_retention(self):
        self.assertIn("rotate 14", self.lines)

    def test_safe_rotation_directives(self):
        for directive in (
            "missingok",
            "notifempty",
            "compress",
            "delaycompress",
            "copytruncate",
        ):
            self.assertIn(directive, self.lines)

    def test_no_process_signals(self):
        forbidden = (
            "postrotate",
            "prerotate",
            "systemctl",
            "kill",
            "pkill",
            "service",
        )
        for line in self.lines:
            for directive in forbidden:
                self.assertFalse(
                    re.search(rf"\b{directive}\b", line),
                    f"Forbidden command or directive: {directive}",
                )

    def test_no_external_include(self):
        self.assertFalse(
            any(line.startswith("include ") for line in self.lines)
        )


if __name__ == "__main__":
    unittest.main()
