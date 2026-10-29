import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
from sweep_main import publish

MAC = "b8:27:eb:e8:36:cd"
OTHER = "00:1c:2b:5a:6d:fd"


class SweepPublisherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.state = root / "presence.json"
        self.metrics = root / "presence.prom"

    def tearDown(self):
        self.tmp.cleanup()

    def sweep(self, devices, timestamp):
        with patch("sweep_main.run_discovery", return_value=devices):
            return publish(self.state, self.metrics, now=timestamp, get_interfaces=lambda: [])

    def test_initial_publication(self):
        counts = self.sweep({MAC: "192.168.2.48"}, 1000)
        self.assertEqual(counts, (1, 1))
        self.assertIn('observed{mac="' + MAC + '"} 1',
                      self.metrics.read_text())
        self.assertEqual(self.state.stat().st_mode & 0o777, 0o600)

    def test_missing_device_keeps_last_seen(self):
        self.sweep({MAC: "192.168.2.48"}, 1000)
        self.sweep({OTHER: "192.168.2.7"}, 1600)
        device = json.loads(self.state.read_text())["devices"][MAC]
        self.assertFalse(device["observed"])
        self.assertEqual(device["last_seen"], 1000)

    def test_hostname_metric_survives_missing_sweep(self):
        interfaces = [{"metric": {
            "address": MAC,
            "target_name": "admin-01",
            "instance": "192.168.2.48:9100",
        }}]
        with patch("sweep_main.run_discovery",
                   return_value={MAC: "192.168.2.48"}):
            publish(self.state, self.metrics, now=1000,
                    get_interfaces=lambda: interfaces)

        self.sweep({OTHER: "192.168.2.7"}, 1600)
        output = self.metrics.read_text()
        self.assertIn(
            f'homelab_lan_presence_host_info{{mac="{MAC}",'
            'target_name="admin-01"} 1', output
        )
        record = json.loads(self.state.read_text())["devices"][MAC]
        self.assertEqual(record["last_seen"], 1000)
        self.assertFalse(record["observed"])

    def test_failed_sweep_preserves_both_files(self):
        self.sweep({MAC: "192.168.2.48"}, 1000)
        original = (self.state.read_bytes(), self.metrics.read_bytes())
        with patch("sweep_main.run_discovery",
                   side_effect=RuntimeError("Scan failed")):
            with self.assertRaises(RuntimeError):
                publish(self.state, self.metrics, now=1600)
        self.assertEqual(
            (self.state.read_bytes(), self.metrics.read_bytes()),
            original,
        )

    def test_mass_disappearance_is_rejected(self):
        devices = {
            f"00:11:22:33:44:{i:02x}": f"192.168.2.{i+1}"
            for i in range(10)
        }
        self.sweep(devices, 1000)
        original = (self.state.read_bytes(), self.metrics.read_bytes())
        with self.assertRaises(ValueError):
            self.sweep(dict(list(devices.items())[:3]), 1600)
        self.assertEqual(
            (self.state.read_bytes(), self.metrics.read_bytes()),
            original,
        )


if __name__ == "__main__":
    unittest.main()
