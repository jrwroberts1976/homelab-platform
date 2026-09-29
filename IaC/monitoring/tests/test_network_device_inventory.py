"""Offline smoke tests for the production LAN inventory exporter.

Run: python3 -m unittest discover -s IaC/monitoring/tests -p 'test_network_device_inventory.py'
No access to live Prometheus, router or Pi-hole required.
"""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = (Path(__file__).resolve().parents[2] /
          "ansible/roles/monitoring_stack/files/network-device-inventory-exporter.py")
spec = importlib.util.spec_from_file_location("network_device_inventory", SOURCE)
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


class InventoryTests(unittest.TestCase):
    def test_only_expected_lan_addresses(self):
        self.assertEqual(inventory.lan_ip("192.168.2.49"), "192.168.2.49")
        self.assertIsNone(inventory.lan_ip("10.10.10.1"))
        self.assertIsNone(inventory.lan_ip("192.168.2.invalid"))

    def test_router_inventory_uses_immutable_read_only_sqlite(self):
        with patch.object(inventory.Path, "is_file", return_value=True), \
             patch.object(inventory.sqlite3, "connect") as connect:
            connection = connect.return_value
            connection.execute.return_value.fetchall.return_value = []
            self.assertEqual(inventory.router_inventory(), [])
        uri = connect.call_args.args[0]
        self.assertIn("mode=ro", uri)
        self.assertIn("immutable=1", uri)
        self.assertTrue(connect.call_args.kwargs["uri"])

    def test_authoritative_os_and_incomplete_scan_handling(self):
        estate = {"assets": [
            {"name": "monitor-01", "address": "192.168.2.52", "state": "active",
             "managed_by_ansible": True, "document_label": "monitor-01",
             "role": "Monitoring", "kind": "vm"},
            {"name": "home-01", "address": "192.168.2.60", "state": "active",
             "managed_by_ansible": False, "document_label": "home-01",
             "role": "Home Assistant", "kind": "vm"}]}
        dns = {"observed_on": "2026-09-25", "devices": {
            "192.168.2.52": {"os_hint": "Windows (DNS indication)"},
            "192.168.2.183": {
                "os_hint": "Windows (DNS indication)",
                "dns_hint": "Windows Update / Microsoft delivery"},
            "192.168.2.252": {"dns_hint": "TP-Link Cloud"}}}
        nmap = {
            "192.168.2.52": {
                "scan_status": "up",
                "os_matches": [{"name": "Linux 5.0-6.2", "accuracy_percent": 97}],
                "ports": [{"state": "open", "port": 22,
                           "protocol": "tcp", "service": "ssh"}]},
            "192.168.2.183": {
                "scan_status": "up",
                "os_matches": [{"name": "Linux 2.6", "accuracy_percent": 50}],
                "ports": []},
            "192.168.2.252": {
                "scan_status": "up",
                "os_matches": [],
                "ports": []}}
        query_results = {
            "homelab_network_host_info": [
                {"metric": {"ip": "192.168.2.52", "hostname": "monitor-01",
                            "mac": "02:00:00:00:02:02"}}],
            "asus_network_asset_info": [
                {"metric": {"ip": "192.168.2.252", "hostname": "light-bulb"}}],
            "homelab_network_host_up": [
                {"metric": {"ip": "192.168.2.52"}, "value": [0, "1"]}],
            "asus_network_asset_up": [],
            "homelab_network_host_last_seen_seconds": [],
            "asus_network_asset_last_seen_seconds": [],
            "homelab_network_host_enrichment_port_info": [
                {"metric": {"ip": "192.168.2.52", "protocol": "tcp",
                            "port": "9100", "service": "node_exporter",
                            "product": "", "version": ""}}],
            'homelab_network_host_os_fingerprint_info{target_name="monitor-01"}': [
                {"metric": {"profiled_ip": "192.168.2.52",
                            "mac": "02:00:00:00:02:02",
                            "nmap_name": "Linux 6.X", "nmap_accuracy": "95%",
                            "nmap_family": "Linux", "nmap_scanned_at":
                            "2026-09-25 07:00 UTC", "nmap_time_basis":
                            "Profile completion", "nmap_services": "22/tcp ssh",
                            "nmap_scan_status": "partial"}},
                # An IP-only match is NOT enough: exclude a previous occupant.
                {"metric": {"profiled_ip": "192.168.2.52",
                            "mac": "de:ad:be:ef:ca:fe",
                            "nmap_name": "Windows", "nmap_accuracy": "99%",
                            "nmap_scanned_at": "2026-09-26 07:00 UTC"}}]}
        def mocked_json(path):
            return estate if path == inventory.ESTATE else dns
        with patch.object(inventory, "load_json", side_effect=mocked_json), \
             patch.object(inventory, "prometheus",
                          side_effect=lambda expr: query_results[expr]), \
             patch.object(inventory, "router_inventory", return_value=[]), \
             patch.object(inventory, "latest_baseline",
                          return_value=(nmap, {"192.168.2.252"},
                                        "20260925T142938Z")):
            hosts = inventory.populate()

        self.assertEqual(hosts["192.168.2.52"]["os"], "Linux (IaC-managed)")
        self.assertEqual(hosts["192.168.2.52"]["os_evidence"], "documented")
        self.assertEqual(hosts["192.168.2.52"]["nmap_name"], "Linux 6.X")
        self.assertEqual(hosts["192.168.2.52"]["nmap_accuracy"], "95%")
        self.assertEqual(hosts["192.168.2.52"]["nmap_time_basis"],
                         "Profile completion")
        self.assertNotEqual(hosts["192.168.2.52"]["nmap_name"], "Windows")
        self.assertEqual(hosts["192.168.2.183"]["nmap_name"], "")

        self.assertEqual(hosts["192.168.2.60"]["os"], "Home Assistant OS 18.2")
        self.assertEqual(hosts["192.168.2.183"]["os_evidence"], "inferred_dns")
        self.assertTrue(hosts["192.168.2.252"]["scan_timed_out"])
        self.assertEqual(hosts["192.168.2.252"]["os"], "Unknown")
        self.assertEqual(len(hosts["192.168.2.52"]["ports"]), 2)
        self.assertEqual(hosts["192.168.2.52"]["ports"][("tcp", 9100)]["service"],
                         "node_exporter")

        metrics = inventory.render(hosts)
        self.assertIn("homelab_network_device_inventory_info", metrics)
        self.assertIn('homelab_network_device_card_info{device_key="mac:02:00:00:00:02:02"', metrics)
        self.assertIn('homelab_network_device_card_online{device_key="mac:02:00:00:00:02:02"', metrics)
        self.assertIn('homelab_network_device_card_port_info{device_key="mac:02:00:00:00:02:02"', metrics)
        self.assertIn("No open ports evidenced", metrics)
        self.assertIn("Not assessed (scan timed out)", metrics)
        self.assertNotIn('homelab_network_device_open_ports_total{ip="192.168.2.252"} 0',
                         metrics)

    def test_mac_card_is_unique_across_ip_changes(self):
        from copy import deepcopy
        template = {
            "ip": "192.168.2.51", "mac": "aa:bb:cc:dd:ee:ff",
            "hostname": "dns-01", "vendor": "", "kind": "lxc",
            "role": "DNS", "os": "Linux", "os_evidence": "documented",
            "os_source": "IaC", "dns_hint": "", "dns_observed": "",
            "online": False, "last_seen": 123, "ports": {},
            "scan_timed_out": False
        }
        moved = deepcopy(template)
        moved.update(ip="192.168.2.88", online=True, last_seen=456)
        metrics = inventory.render({
            template["ip"]: template, moved["ip"]: moved
        })
        cards = [line for line in metrics.splitlines()
                 if line.startswith("homelab_network_device_card_info{")]
        self.assertEqual(len(cards), 1)
        self.assertIn('device_key="mac:aa:bb:cc:dd:ee:ff"', cards[0])
        self.assertIn('ip="192.168.2.88"', cards[0])

    def test_display_hostname_and_ip_fallback_never_mac(self):
        def host(ip, mac, hostname):
            return {
                "ip": ip, "mac": mac, "hostname": hostname,
                "vendor": "Generic Manufacturer", "kind": "network",
                "role": "", "os": "Unknown", "os_evidence": "unknown",
                "os_source": "Not determined", "dns_hint": "",
                "dns_observed": "", "online": True, "last_seen": 999,
                "ports": {}, "scan_timed_out": True
            }

        records = {
            "192.168.2.6": host(
                "192.168.2.6", "aa:bb:cc:00:00:01", "laptop"),
            "192.168.2.7": host(
                "192.168.2.7", "aa:bb:cc:00:00:02", "laptop"),
            "192.168.2.8": host(
                "192.168.2.8", "aa:bb:cc:00:00:03", ""),
        }
        metrics = inventory.render(records)
        cards = [line for line in metrics.splitlines()
                 if line.startswith("homelab_network_device_card_info{")]
        self.assertEqual(len(cards), 3)
        self.assertTrue(any('hostname="laptop (192.168.2.6)"' in x
                            for x in cards))
        self.assertTrue(any('hostname="laptop (192.168.2.7)"' in x
                            for x in cards))
        self.assertTrue(any('hostname="192.168.2.8"' in x
                            for x in cards))
        self.assertFalse(any('hostname="aa:bb' in x for x in cards))

    def test_prometheus_labels_escape(self):
        self.assertEqual(inventory.esc('foo\n"bar"'),
                         'foo \\"bar\\"')


if __name__ == "__main__":
    unittest.main()
