#!/usr/bin/env python3
"""Offline temporal DHCP lease snapshot safety tests."""
import importlib.util
import pathlib
import unittest

P = pathlib.Path(__file__).resolve().parents[1] / "scripts/passive_os_lease_snapshot.py"
SPEC = importlib.util.spec_from_file_location("lease_snapshot", P)
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)
T = 1793969000


def lease(expiry, mac="ec:91:61:9c:a4:45", ip="192.168.2.113", host="private-device"):
    return f"{expiry} {mac} {ip} {host} *\n"


class LeaseSnapshotTests(unittest.TestCase):
    def test_never_backdates_lease(self):
        d = m.snapshot(lease(T + 86400), T)
        x = d["leases"]["192.168.2.113"][0]
        self.assertEqual(x["valid_from"], T)
        self.assertEqual(x["valid_until"], T + 300)

    def test_expiry_bounds_window(self):
        d = m.snapshot(lease(T + 60), T)
        self.assertEqual(d["leases"]["192.168.2.113"][0]["valid_until"], T + 60)

    def test_expired_lease_excluded(self):
        self.assertEqual(m.snapshot(lease(T - 1), T)["leases"], {})

    def test_zero_expiry_not_misread_as_current(self):
        self.assertEqual(m.snapshot(lease(0), T)["leases"], {})

    def test_hostname_never_exported(self):
        d = m.snapshot(lease(T + 1000, host="private-device"), T)
        self.assertNotIn("private-device", str(d))

    def test_duplicate_mac_conflict_excluded(self):
        text = lease(T + 1000) + lease(T + 1000, mac="00:11:22:33:44:55")
        d = m.snapshot(text, T)
        self.assertEqual(d["leases"], {})
        self.assertEqual(d["conflicting_ips"], ["192.168.2.113"])

    def test_bad_mac_or_nonlan_ip_ignored(self):
        text = lease(T + 1000, mac="bad") + lease(T + 1000, ip="8.8.8.8")
        self.assertEqual(m.snapshot(text, T)["leases"], {})

    def test_window_greater_than_five_minutes_refused(self):
        with self.assertRaises(ValueError):
            m.snapshot(lease(T + 1000), T, 301)

    def test_lease_line_limit(self):
        with self.assertRaises(ValueError):
            m.parse_leases([lease(T + 1000)] * 1025, T)

    def test_input_size_cap(self):
        with self.assertRaises(ValueError):
            m.snapshot("x" * (m.MAX_INPUT_BYTES + 1), T)

    def test_invalid_time_refused(self):
        with self.assertRaises(ValueError):
            m.snapshot(lease(T + 1000), -1)


if __name__ == "__main__":
    unittest.main()
