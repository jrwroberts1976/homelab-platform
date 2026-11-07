#!/usr/bin/env python3
"""Offline checks of one-shot passive OS textfile publisher."""
import hashlib
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from passive_os_sensor_metrics import validate, metrics_for, candidate_summary


def batch_for(observations):
    canonical = json.dumps(observations, sort_keys=True, separators=(",", ":")).encode()
    return {
        "protocol": 1, "batch_id": "a" * 64,
        "digest": hashlib.sha256(canonical).hexdigest(),
        "observations": observations,
    }


class PassiveOSMetricsTests(unittest.TestCase):
    def setUp(self):
        self.events = [
            {"src_ip": "192.168.2.113", "event_type": "http",
             "timestamp": 1794027660, "os_family_hint": "Linux"},
            {"src_ip": "192.168.2.113", "event_type": "http",
             "timestamp": 1794027661, "os_family_hint": "Linux"},
            {"src_ip": "192.168.2.114", "event_type": "dns",
             "timestamp": 1794027661},
        ]

    def test_valid_wire_and_metrics(self):
        raw = json.dumps(batch_for(self.events)).encode()
        batch = validate(raw)
        payload, count = metrics_for(batch)
        self.assertEqual(count, 1)
        self.assertIn(b'os_family="Linux"', payload)
        self.assertIn(b'confidence="low",mac_attribution="unverified"', payload)
        self.assertIn(b'candidate_observations{', payload)
        self.assertIn(b'} 2\n', payload)

    def test_dry_run_summary_minimised(self):
        result = candidate_summary(batch_for(self.events))
        self.assertEqual(result, [{
            "src_ip": "192.168.2.113", "os_family_hint": "Linux",
            "observations": 2, "confidence": "low",
            "mac_attribution": "unverified",
        }])
        self.assertNotIn("http_user_agent", repr(result))

    def test_digest_mismatch_rejected(self):
        batch = batch_for(self.events)
        batch["digest"] = "b" * 64
        with self.assertRaises(ValueError):
            validate(json.dumps(batch).encode())

    def test_raw_user_agent_rejected(self):
        batch = batch_for(self.events)
        batch["observations"][0]["http_user_agent"] = "private"
        with self.assertRaises(ValueError):
            validate(json.dumps(batch).encode())

    def test_conflicting_family_stays_separate(self):
        events = self.events[:2]
        events[1] = dict(events[1], os_family_hint="Windows")
        payload, count = metrics_for(batch_for(events))
        self.assertEqual(count, 2)
        self.assertIn(b'os_family="Windows"', payload)
        self.assertIn(b'os_family="Linux"', payload)

    def test_empty_candidates_not_authoritative(self):
        payload, count = metrics_for(batch_for([self.events[2]]))
        self.assertEqual(count, 0)
        self.assertNotIn(b'candidate_info{', payload)


if __name__ == "__main__":
    unittest.main()
