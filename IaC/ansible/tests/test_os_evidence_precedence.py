#!/usr/bin/env python3
"""Offline evidence-precedence tests: no SSH, scans, Zabbix, or metrics writes."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from os_evidence_precedence import resolve

IP = "192.168.2.186"
MAC = "24:b2:b9:30:f8:55"
WIN = [{"src_ip": IP, "os_family_hint": "Windows", "observations": 1}]
PARTIAL = {"status": "partial", "profiled_ip": IP,
           "last_error": "os_evidence_missing",
           "profile": {"tcp": {"os_matches": [], "ports": []}, "errors": {}}}
FOUND = {"status": "complete", "profiled_ip": IP,
         "profile": {"tcp": {"os_matches": [{"name": "Example OS"}]}}}


class EvidencePrecedenceTests(unittest.TestCase):
    def test_zabbix_overrides_both_other_evidence(self):
        r = resolve(IP, MAC, "zabbix_os_authoritative", FOUND, WIN)
        self.assertEqual(r["os_source"], "zabbix")
        self.assertEqual(r["confidence"], "authoritative")
        self.assertIsNone(r["os_family"])

    def test_agent_without_os_is_not_passively_overridden(self):
        r = resolve(IP, MAC, "zabbix_without_os", PARTIAL, WIN)
        self.assertEqual(r["status"], "managed_os_missing")
        self.assertEqual(r["os_source"], "unknown")

    def test_ambiguous_identity_refuses_os(self):
        r = resolve(IP, MAC, "ambiguous", FOUND, WIN)
        self.assertEqual(r["status"], "identity_ambiguous")
        self.assertIsNone(r["os_family"])

    def test_nmap_os_match_precedes_passive(self):
        r = resolve(IP, MAC, "unmatched_inventory", FOUND, WIN)
        self.assertEqual(r["os_source"], "nmap")
        self.assertEqual(r["confidence"], "candidate")

    def test_partial_nmap_falls_back_to_low_confidence_hint(self):
        r = resolve(IP, MAC, "unmatched_inventory", PARTIAL, WIN)
        self.assertEqual(r["os_family"], "Windows")
        self.assertEqual(r["confidence"], "low")
        self.assertEqual(r["attribution"], "historical_ip_unverified")
        self.assertEqual(r["status"], "passive_candidate_only")

    def test_no_evidence_stays_unknown(self):
        r = resolve(IP, MAC, "unmatched_inventory", PARTIAL, [])
        self.assertEqual(r["status"], "nmap_partial_no_os")
        self.assertEqual(r["os_source"], "unknown")

    def test_conflicting_passive_hints_do_not_choose_winner(self):
        hints = WIN + [{"src_ip": IP, "os_family_hint": "Linux",
                        "observations": 10}]
        r = resolve(IP, MAC, "unmatched_inventory", PARTIAL, hints)
        self.assertEqual(r["status"], "passive_conflicting_hints")
        self.assertIsNone(r["os_family"])

    def test_wrong_ip_hints_cannot_label_laptop(self):
        hint = [{"src_ip": "192.168.2.125", "os_family_hint": "Linux",
                 "observations": 6}]
        r = resolve(IP, MAC, "unmatched_inventory", PARTIAL, hint)
        self.assertEqual(r["status"], "nmap_partial_no_os")

    def test_stale_nmap_evidence_not_promoted(self):
        stale = dict(FOUND, profile={"tcp": {"os_matches": [{"name": "OS"}]},
                                    "tcp_evidence_stale": True})
        r = resolve(IP, MAC, "unmatched_inventory", stale, WIN)
        self.assertEqual(r["os_source"], "http_user_agent")

    def test_wrong_ip_nmap_evidence_not_promoted(self):
        wrong_ip = dict(FOUND, profiled_ip="192.168.2.125")
        r = resolve(IP, MAC, "unmatched_inventory", wrong_ip, WIN)
        self.assertEqual(r["os_source"], "http_user_agent")

    def test_invalid_classification_fails_closed(self):
        with self.assertRaises(ValueError):
            resolve(IP, MAC, "not_a_classification", PARTIAL, WIN)


if __name__ == "__main__":
    unittest.main()
