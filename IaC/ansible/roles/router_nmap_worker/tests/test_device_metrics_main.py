"""Tests for safe publication of device metrics."""

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "files")
)

from device_metrics_main import publish


class DeviceMetricsPublisherTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        root = Path(self.temp.name)
        self.collector = root / "devices.json"
        self.profiles = root / "profiles.json"
        self.output = root / "homelab_router_devices.prom"

        self.collector.write_text(json.dumps({
            "schema_version": 1,
            "devices": {
                "aa:bb:cc:dd:ee:01": {
                    "status": "baseline",
                    "last_ip": "192.168.2.20",
                    "hostname": "existing-host",
                }
            },
        }))

    def test_successful_atomic_publication(self):
        self.assertEqual(
            publish(self.collector, self.profiles, self.output, now=1234),
            1,
        )
        result = self.output.read_text()
        self.assertIn('hostname="existing-host"', result)
        self.assertIn(
            "homelab_router_device_metrics_generated_timestamp_seconds 1234",
            result,
        )
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o644)
        self.assertEqual(
            list(self.output.parent.glob(".homelab_router_devices.*")),
            [],
        )

    def test_invalid_source_preserves_existing_metrics(self):
        self.output.write_text("PREVIOUS_VALID_METRICS\n")
        self.collector.write_text("{invalid")

        with self.assertRaises(json.JSONDecodeError):
            publish(self.collector, self.profiles, self.output)

        self.assertEqual(
            self.output.read_text(),
            "PREVIOUS_VALID_METRICS\n",
        )

    def test_invalid_profile_preserves_existing_metrics(self):
        self.output.write_text("PREVIOUS_VALID_METRICS\n")
        self.profiles.write_text(json.dumps({
            "schema_version": 1,
            "profiles": {
                "aa:bb:cc:dd:ee:01": {"status": "unexpected"}
            },
        }))

        with self.assertRaises(ValueError):
            publish(self.collector, self.profiles, self.output)

        self.assertEqual(
            self.output.read_text(),
            "PREVIOUS_VALID_METRICS\n",
        )

    def test_rejects_unexpected_output_filename(self):
        with self.assertRaises(ValueError):
            publish(
                self.collector,
                self.profiles,
                self.output.parent / "other.prom",
            )


    def test_publisher_includes_adapter_manufacturer(self):
        data = json.loads(self.collector.read_text())
        device = data["devices"].pop("aa:bb:cc:dd:ee:01")
        data["devices"]["24:b2:b9:30:f8:55"] = device
        self.collector.write_text(json.dumps(data))

        vendors = self.output.parent / "nmap-mac-prefixes"
        vendors.write_text("24B2B9 Example Manufacturer" + chr(10))

        publish(
            self.collector, self.profiles, self.output,
            now=1234, vendors_path=vendors,
        )
        self.assertIn(
            'vendor="Example Manufacturer"',
            self.output.read_text(),
        )

    def test_missing_vendor_database_preserves_metrics(self):
        self.output.write_text("PREVIOUS_VALID_METRICS\\n")
        with self.assertRaises(FileNotFoundError):
            publish(
                self.collector, self.profiles, self.output,
                vendors_path=self.output.parent / "missing-vendors",
            )
        self.assertEqual(
            self.output.read_text(),
            "PREVIOUS_VALID_METRICS\\n",
        )


if __name__ == "__main__":
    unittest.main()
