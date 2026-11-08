import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "scripts")
)

from router_dhcp_infinite_recovery import (
    ORIGINAL_RANGE,
    INFINITE_RANGE,
    sha256,
    recovery_decision,
)


ORIGINAL = (ORIGINAL_RANGE + "\n").encode()
CANDIDATE = (INFINITE_RANGE + "\n").encode()

ORIGINAL_SHA = sha256(ORIGINAL)
CANDIDATE_SHA = sha256(CANDIDATE)


class RecoveryTests(unittest.TestCase):

    def decide(self, active, backup=ORIGINAL):
        return recovery_decision(
            active,
            backup,
            ORIGINAL_SHA,
            CANDIDATE_SHA,
        )

    def test_candidate_can_be_restored(self):
        self.assertEqual(
            self.decide(CANDIDATE),
            "RESTORE_APPROVED",
        )

    def test_already_original(self):
        self.assertEqual(
            self.decide(ORIGINAL),
            "ALREADY_ORIGINAL",
        )

    def test_unknown_configuration_refused(self):
        self.assertEqual(
            self.decide(b"unexpected change\n"),
            "REFUSE_UNKNOWN_CONFIGURATION",
        )

    def test_corrupt_backup_refused(self):
        self.assertEqual(
            self.decide(CANDIDATE, b"corrupt backup"),
            "REFUSE_BACKUP_MISMATCH",
        )

    def test_invalid_expected_original_refused(self):
        malformed = b"wrong original config\n"
        self.assertEqual(
            recovery_decision(
                CANDIDATE,
                malformed,
                sha256(malformed),
                CANDIDATE_SHA,
            ),
            "REFUSE_INVALID_BACKUP",
        )


if __name__ == "__main__":
    unittest.main()
