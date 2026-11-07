#!/usr/bin/env python3
"""Offline DHCP finalisation tests."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "scripts")
)

import router_dhcp_infinite_finalise as finaliser


class FinalisationTests(unittest.TestCase):

    def decide(self, active, healthy=True, rollback=False):
        return finaliser.finalisation_decision(
            active, healthy, rollback
        )

    def test_approved_candidate(self):
        with patch.object(
            finaliser, "sha256",
            return_value=finaliser.CANDIDATE_SHA,
        ):
            self.assertEqual(
                self.decide(b"synthetic candidate"),
                "FINALISATION_ALLOWED",
            )

    def test_rollback_already_started(self):
        self.assertEqual(
            self.decide(b"anything", rollback=True),
            "REFUSE_ROLLBACK_STARTED",
        )

    def test_unknown_configuration(self):
        self.assertEqual(
            self.decide(b"unexpected configuration"),
            "REFUSE_CONFIGURATION_MISMATCH",
        )

    def test_unhealthy_service(self):
        with patch.object(
            finaliser, "sha256",
            return_value=finaliser.CANDIDATE_SHA,
        ):
            self.assertEqual(
                self.decide(b"synthetic candidate", healthy=False),
                "REFUSE_UNHEALTHY_SERVICE",
            )


if __name__ == "__main__":
    unittest.main()
