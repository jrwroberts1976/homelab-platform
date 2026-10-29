import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))

from presence_state import empty_state, merge_sweep
from presence_metrics import render_metrics

MAC = "b8:27:eb:e8:36:cd"
OTHER = "00:1c:2b:5a:6d:fd"


class PresenceMetricsTests(unittest.TestCase):
    def setUp(self):
        self.first = merge_sweep(
            empty_state(), {MAC: "192.168.2.48"}, 1000
        )

    def test_online_device(self):
        output = render_metrics(self.first)
        self.assertIn('homelab_lan_presence_observed{mac="' + MAC + '"} 1', output)
        self.assertIn("homelab_lan_presence_last_sweep_seconds 1000", output)

    def test_missing_device_retains_last_seen(self):
        state = merge_sweep(
            self.first, {OTHER: "192.168.2.7"}, 1600
        )
        output = render_metrics(state)
        self.assertIn('homelab_lan_presence_observed{mac="' + MAC + '"} 0', output)
        self.assertIn(
            'homelab_lan_presence_last_seen_seconds{mac="' + MAC + '"} 1000',
            output,
        )

    def test_returning_device_updates_ip_and_timestamp(self):
        state = merge_sweep(
            self.first, {MAC: "192.168.2.49"}, 1600
        )
        output = render_metrics(state)
        self.assertIn('ip="192.168.2.49"', output)
        self.assertIn(
            'homelab_lan_presence_last_seen_seconds{mac="' + MAC + '"} 1600',
            output,
        )


if __name__ == "__main__":
    unittest.main()
