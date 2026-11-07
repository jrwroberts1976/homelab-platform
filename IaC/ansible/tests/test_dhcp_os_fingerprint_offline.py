#!/usr/bin/env python3
"""Tests for synthetic, offline-only DHCP fingerprints."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from dhcp_os_fingerprint_offline import normalise, process


FIXTURE = {
    "timestamp": 1794000000,
    "src_ip": "192.168.2.150",
    "mac": "aa:bb:cc:dd:ee:ff",
    "option55": [1, 3, 6, 15, 119, 252],
    "option60": "SYNTHETIC-TEST-CLIENT",
}


class DhcpFingerprintTests(unittest.TestCase):
    def test_valid_observation(self):
        result = normalise(FIXTURE)
        self.assertEqual(result["status"], "fingerprint_only")
        self.assertEqual(result["option55"], FIXTURE["option55"])
        self.assertIsNone(result["os_family"])
        self.assertEqual(result["confidence"], "none")

    def test_no_plaintext_vendor_leakage(self):
        result = normalise(FIXTURE)
        self.assertNotIn(
            FIXTURE["option60"], str(result)
        )
        self.assertEqual(len(result["option60_sha256"]), 64)

    def test_outside_lan_rejected(self):
        with self.assertRaises(ValueError):
            normalise(dict(FIXTURE, src_ip="192.168.1.150"))

    def test_duplicate_prl_rejected(self):
        with self.assertRaises(ValueError):
            normalise(dict(FIXTURE, option55=[1, 3, 3]))

    def test_boolean_option_rejected(self):
        with self.assertRaises(ValueError):
            normalise(dict(FIXTURE, option55=[1, True, 6]))

    def test_extra_fields_rejected(self):
        with self.assertRaises(ValueError):
            normalise(dict(FIXTURE, hostname="private-device"))

    def test_empty_vendor_rejected(self):
        with self.assertRaises(ValueError):
            normalise(dict(FIXTURE, option60=""))

    def test_no_automatic_os_identification(self):
        result = process({"observations": [FIXTURE]})
        self.assertEqual(result["mode"], "offline_synthetic_only")
        self.assertEqual(
            result["observations"][0]["attribution"],
            "fixture_claim_unverified",
        )

    def test_record_ceiling(self):
        with self.assertRaises(ValueError):
            process({"observations": [FIXTURE] * 2001})


if __name__ == "__main__":
    unittest.main()
