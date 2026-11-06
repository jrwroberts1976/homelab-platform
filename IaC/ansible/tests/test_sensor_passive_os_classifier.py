#!/usr/bin/env python3
"""Offline-only passive OS identification tests; no capture, network, or scans."""
import importlib.util
import pathlib
import unittest

SOURCE = (pathlib.Path(__file__).resolve().parents[1]
          / "scripts/sensor_passive_os_classifier.py")
SPEC = importlib.util.spec_from_file_location("passive_os", SOURCE)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

T = 1793950000
LEASES = {
    "192.168.2.113": [{"mac": "ec:91:61:9c:a4:45",
                       "valid_from": T - 3600, "valid_until": T + 3600}],
    "192.168.2.125": [{"mac": "a4:77:33:5f:94:fe",
                       "valid_from": T - 3600, "valid_until": T + 3600}],
}


def event(ip="192.168.2.113", kind="http", ua="Mozilla/5.0 (X11; CrOS x86_64 1)",
          when=T):
    return {"src_ip": ip, "event_type": kind,
            "http_user_agent": ua, "timestamp": when}


class PassiveClassificationTests(unittest.TestCase):
    def test_chromeos_from_user_agent_is_low_confidence(self):
        data = mod.classify([event()] * 7, LEASES)
        device = data["devices"][0]
        self.assertEqual(device["os_family"], "ChromeOS")
        self.assertEqual(device["confidence"], "low")
        self.assertEqual(device["observations"], 7)
        self.assertNotIn("http_user_agent", device)

    def test_embedded_linux_candidate_not_exact_version(self):
        d = mod.classify(
            [event("192.168.2.125", ua="Linux; U; embedded")], LEASES
        )["devices"][0]
        self.assertEqual(d["os_family"], "Linux")
        self.assertNotIn("version", d)

    def test_dns_tls_quic_alone_cannot_identify_os(self):
        events = [event(kind=k, ua="Windows NT 10.0")
                  for k in ("dns", "tls", "quic")]
        d = mod.classify(events, LEASES)["devices"][0]
        self.assertEqual((d["os_family"], d["status"]),
                         ("unknown", "insufficient"))

    def test_conflicting_user_agents_fail_closed(self):
        d = mod.classify([event(ua="Windows NT 10.0"),
                          event(ua="Android 15")], LEASES)["devices"][0]
        self.assertEqual((d["os_family"], d["status"]),
                         ("unknown", "conflicting"))

    def test_lease_expiry_blocks_stale_ip_identity(self):
        d = mod.classify([event(when=T + 3600)], LEASES)
        self.assertEqual(d["devices"], [])
        self.assertEqual(d["skipped_unattributed"], 1)

    def test_ambiguous_ip_mac_lease_blocks_attribution(self):
        leases = dict(LEASES)
        leases["192.168.2.113"] = (
            list(LEASES["192.168.2.113"]) + [{
                "mac": "00:11:22:33:44:55",
                "valid_from": T - 100, "valid_until": T + 100,
            }]
        )
        self.assertEqual(mod.classify([event()], leases)["devices"], [])

    def test_gateway_and_public_ips_rejected(self):
        events = [event(ip=ip) for ip in
                  ("192.168.2.1", "8.8.8.8", "192.168.2.255")]
        self.assertEqual(mod.classify(events, LEASES)["devices"], [])

    def test_processing_cap(self):
        with self.assertRaises(ValueError):
            mod.classify([event(), event()], LEASES, max_events=1)

    def test_bad_or_missing_agent_is_unknown(self):
        d = mod.classify([event(ua=None)], LEASES)["devices"][0]
        self.assertEqual(d["os_family"], "unknown")
        self.assertEqual(d["observations"], 0)


if __name__ == "__main__":
    unittest.main()
