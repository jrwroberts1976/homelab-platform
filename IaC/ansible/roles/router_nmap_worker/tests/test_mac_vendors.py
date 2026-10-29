"""Regression tests for manufacturer identification."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "files")
)

from mac_vendors import load_vendors, lookup_vendor


class MacVendorTests(unittest.TestCase):
    def test_nmap_database_format(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "nmap-mac-prefixes"
            path.write_text(
                "# Sample database\n"
                "24B2B9 Example Network Devices\n"
                "000001 Xerox\n"
            )
            vendors = load_vendors(path)
            self.assertEqual(
                vendors["24B2B9"], "Example Network Devices"
            )

    def test_normal_mac_lookup(self):
        vendors = {"24B2B9": "Example Vendor"}
        self.assertEqual(
            lookup_vendor("24:b2:b9:30:f8:55", vendors),
            "Example Vendor",
        )

    def test_randomised_mac_has_no_vendor(self):
        self.assertIsNone(
            lookup_vendor("02:11:22:33:44:55", {"021122": "Incorrect"})
        )

    def test_multicast_mac_has_no_vendor(self):
        self.assertIsNone(
            lookup_vendor("01:00:5e:00:00:01", {"01005E": "Incorrect"})
        )

    def test_unknown_or_invalid_mac(self):
        self.assertIsNone(lookup_vendor("24:b2:b9:30:f8:55", {}))
        self.assertIsNone(lookup_vendor("invalid", {}))


if __name__ == "__main__":
    unittest.main()
