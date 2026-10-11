"""Tests for MAC-keyed Prometheus device metrics."""

import sys
import unittest
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "files")
)
from device_metrics import render_metrics, label


class DeviceMetricsTests(unittest.TestCase):
    def setUp(self):
        self.mac = "aa:bb:cc:dd:ee:01"
        self.collector = {
            "schema_version": 1,
            "devices": {
                self.mac: {
                    "status": "baseline",
                    "last_ip": "192.168.2.20",
                    "hostname": "example-host",
                    "last_inventory_seen": 1000,
                }
            },
        }
        self.worker = {"schema_version": 1, "profiles": {}}

    def test_baseline_has_identity_but_no_scan_result(self):
        output = render_metrics(self.collector, self.worker)
        self.assertIn('mac="aa:bb:cc:dd:ee:01"', output)
        self.assertIn('discovery_status="baseline"', output)
        self.assertNotIn("homelab_router_device_scan_state{", output)

    def test_completed_scan_is_reported(self):
        self.collector["devices"][self.mac]["status"] = "pending"
        self.worker["profiles"][self.mac] = {
            "status": "complete",
            "profile": {
                "tcp": {"os_matches": [], "ports": []},
                "udp": {"os_matches": [], "ports": []},
            },
        }
        output = render_metrics(self.collector, self.worker)
        self.assertIn('status="complete"} 1', output)

    def test_invalid_mac_is_rejected(self):
        self.collector["devices"]["invalid"] = {}
        with self.assertRaises(ValueError):
            render_metrics(self.collector, self.worker)

    def test_untrusted_hostname_is_escaped(self):
        self.assertEqual(label('host"name'), '"host\\"name"')


    def test_verified_tcp_port_and_os_estimate(self):
        self.worker["profiles"][self.mac] = {
            "status": "complete",
            "profile": {
                "tcp": {
                    "os_matches": [
                        {"name": "Linux 6.x", "accuracy": "93"}
                    ],
                    "ports": [{
                        "port": 22,
                        "state": "open",
                        "service": {"name": "ssh", "product": "OpenSSH"},
                    }],
                },
                "udp": {"os_matches": [], "ports": []},
            },
        }
        output = render_metrics(self.collector, self.worker)
        self.assertIn('port="22",state="open"', output)
        self.assertIn('os="Linux 6.x"} 93', output)

    def test_inconclusive_udp_is_not_confirmed_open(self):
        self.worker["profiles"][self.mac] = {
            "status": "partial",
            "profile": {
                "tcp": {"os_matches": [], "ports": []},
                "udp": {
                    "os_matches": [],
                    "ports": [{
                        "port": 161,
                        "state": "open|filtered",
                        "service": {"name": "snmp"},
                    }],
                },
            },
        }
        output = render_metrics(self.collector, self.worker)
        self.assertIn('port="161",state="open|filtered"', output)
        self.assertNotIn('port="161",state="open"', output)

    def test_failed_scan_has_no_service_or_os_findings(self):
        self.worker["profiles"][self.mac] = {
            "status": "failed",
            "last_error": "Target unavailable",
        }
        output = render_metrics(self.collector, self.worker)
        self.assertIn('status="failed"} 1', output)
        self.assertNotIn("homelab_router_device_port_info{", output)
        self.assertNotIn(
            "homelab_router_device_os_estimate_accuracy_percent{",
            output,
        )

    def test_registered_adapter_manufacturer(self):
        device = self.collector["devices"].pop(self.mac)
        self.collector["devices"]["24:b2:b9:30:f8:55"] = device
        output = render_metrics(
            self.collector, self.worker,
            vendors={"24B2B9": "Example Manufacturer"},
        )
        self.assertIn('vendor="Example Manufacturer"', output)

    def test_randomised_mac_has_no_manufacturer(self):
        output = render_metrics(
            self.collector, self.worker,
            vendors={"AABBCC": "Misleading Manufacturer"},
        )
        self.assertNotIn(
            "homelab_router_device_adapter_vendor_info{", output
        )


    def test_ranked_os_matches_from_both_scans(self):
        self.worker["profiles"][self.mac] = {
            "status": "complete",
            "profile": {
                "tcp": {
                    "os_matches": [
                        {"name": "Linux 6.x", "accuracy": "93"},
                        {"name": "FreeBSD", "accuracy": "81"},
                    ],
                    "ports": [],
                },
                "udp": {
                    "os_matches": [
                        {"name": "Linux 5.x", "accuracy": "76"},
                    ],
                    "ports": [],
                },
            },
        }
        output = render_metrics(self.collector, self.worker)
        self.assertIn(
            'protocol="tcp",rank="1",os="Linux 6.x"} 93',
            output,
        )
        self.assertIn(
            'protocol="tcp",rank="2",os="FreeBSD"} 81',
            output,
        )
        self.assertIn(
            'protocol="udp",rank="1",os="Linux 5.x"} 76',
            output,
        )

    def test_invalid_os_accuracy_is_not_published(self):
        self.worker["profiles"][self.mac] = {
            "status": "partial",
            "profile": {
                "tcp": {
                    "os_matches": [
                        {"name": "Invalid", "accuracy": "unknown"},
                        {"name": "Valid", "accuracy": "82"},
                    ],
                    "ports": [],
                },
            },
        }
        output = render_metrics(self.collector, self.worker)
        self.assertNotIn('os="Invalid"}', output)
        self.assertIn(
            'protocol="tcp",rank="2",os="Valid"} 82',
            output,
        )


if __name__ == "__main__":
    unittest.main()
