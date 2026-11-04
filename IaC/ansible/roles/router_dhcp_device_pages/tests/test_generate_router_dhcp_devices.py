"""Offline, no-network regression tests for router-01 DHCP device dashboard source."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).parents[1] / "files" / "generate_router_dhcp_devices.py"
spec = importlib.util.spec_from_file_location("router_dhcp_pages", SOURCE)
pages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pages)

MAC_A = "02:11:22:33:44:55"
MAC_B = "02:11:22:33:44:66"


class DHCPDevicePages(unittest.TestCase):
    def ack(self, mac=MAC_A, ip="192.168.2.101", seen=100, host="tablet"):
        return pages.parse_ack(
            "dnsmasq-dhcp[213]: DHCPACK(eth0) " + ip + " " + mac + " " + host,
            seen)

    def test_trusted_router_ack_and_mac_normalisation(self):
        event = self.ack(mac=MAC_A.upper())
        self.assertEqual(event["mac"], MAC_A)
        self.assertEqual(event["hostname"], "tablet")
        self.assertEqual(event["ip"], "192.168.2.101")

    def test_refuse_wrong_interface_or_unsafe_address(self):
        self.assertIsNone(pages.parse_ack(
            "DHCPACK(br0) 192.168.2.101 " + MAC_A, 100))
        self.assertIsNone(self.ack(ip="192.168.1.101"))
        self.assertIsNone(self.ack(ip="192.168.2.1"))
        self.assertIsNone(self.ack(ip="192.168.2.255"))
        self.assertIsNone(self.ack(mac="01:11:22:33:44:55"))
        self.assertIsNone(self.ack(mac="00:00:00:00:00:00"))
        self.assertIsNone(pages.parse_ack("DHCPDISCOVER(eth0) 192.168.2.101 "+MAC_A, 100))
        self.assertIsNone(pages.parse_ack("DHCPACK(eth0) 192.168.2.101 "+MAC_A, -1))

    def test_dhcp_ip_changed_keeps_original_mac_page_uid(self):
        state = {"schema_version": 1, "devices": {}}
        one, created = pages.merge_events(state, [self.ack()])
        uid = pages.uid_for(MAC_A)
        self.assertEqual(created, 1)
        two, created = pages.merge_events(one, [
            self.ack(ip="192.168.2.105", seen=300),
            self.ack(ip="192.168.2.100", seen=150)])
        self.assertEqual(created, 0)
        self.assertEqual(two["devices"][MAC_A]["ip"], "192.168.2.105")
        self.assertEqual(two["devices"][MAC_A]["first_seen_ns"], 100)
        self.assertEqual(uid, pages.uid_for(MAC_A))

    def test_dhcp_renew_is_idempotent(self):
        state = {"schema_version": 1, "devices": {}}
        one, created = pages.merge_events(state, [self.ack()])
        two, created_again = pages.merge_events(one, [self.ack()])
        self.assertEqual(created, 1)
        self.assertEqual(created_again, 0)
        self.assertEqual(one, two)

    def test_canary_only_creates_one_and_never_drops_an_existing_record(self):
        state = {"schema_version": 1, "devices": {}}
        a = self.ack(mac=MAC_A, seen=100)
        b = self.ack(mac=MAC_B, seen=200)
        limited, count = pages.merge_events(state, [a, b], max_new=1)
        self.assertEqual(count, 1)
        self.assertIn(MAC_A, limited["devices"])
        self.assertNotIn(MAC_B, limited["devices"])
        full, count = pages.merge_events(limited, [a, b])
        self.assertEqual(count, 1)
        self.assertEqual(set(full["devices"]), {MAC_A, MAC_B})
        later, count = pages.merge_events(full, [])
        self.assertEqual(count, 0)
        self.assertEqual(later, full)

    def test_os_remains_inferred_and_never_reuses_wrong_ip_profile(self):
        profiles = {"profiles": {MAC_A: {
            "profiled_ip": "192.168.2.101",
            "profile": {"tcp": {
                "os_matches": [{"name": "Linux 5.x", "accuracy": "92"}],
                "ports": [{"port": 22, "service": {"name": "ssh"}}]}}}}}
        found, status, ports = pages.os_and_ports(MAC_A, "192.168.2.101", profiles)
        self.assertIn("Nmap inferred:", found)
        self.assertIn("92%", found)
        self.assertEqual(status, "inferred")
        self.assertEqual(ports, ["22/tcp ssh"])
        unknown, status, ports = pages.os_and_ports(MAC_A, "192.168.2.105", profiles)
        self.assertIn("awaiting", unknown)
        self.assertEqual(status, "pending")
        self.assertEqual(ports, [])

    def test_dashboard_contains_real_source_and_no_html_injected(self):
        event = self.ack()
        lease = {"ip": event["ip"], "hostname": "tablet",
                 "first_seen_ns": 100, "last_seen_ns": 100 * 10**9}
        inventory = {"192.168.2.101": {"mac": MAC_A, "vendor": "<bad>|x",
                                        "online": True}}
        result = pages.dashboard(MAC_A, lease, inventory, {"profiles": {}})
        self.assertEqual(result["uid"], pages.uid_for(MAC_A))
        self.assertEqual(result["panels"][3]["datasource"]["uid"], "loki")
        self.assertIn(MAC_A, result["panels"][3]["targets"][0]["expr"])
        self.assertNotIn("<bad>", result["panels"][0]["options"]["content"])
        self.assertIn("Unknown", result["panels"][0]["options"]["content"])

    def test_read_only_dry_run_and_idempotent_apply(self):
        with tempfile.TemporaryDirectory() as root:
            state_file = Path(root) / "state.json"
            output_dir = Path(root) / "pages"
            event = self.ack(seen=100 * 10**9)
            state = pages.load_state(state_file)
            with self.assertRaises(ValueError):
                pages.reconcile([], {}, {"profiles": {}}, state,
                                output_dir, state_file)
            preview = pages.reconcile([event], {}, {"profiles": {}}, state,
                                      output_dir, state_file)
            self.assertEqual(preview["new_devices"], 1)
            self.assertFalse(state_file.exists())
            self.assertFalse(output_dir.exists())
            output_dir.mkdir()
            first = pages.reconcile([event], {}, {"profiles": {}}, state,
                                    output_dir, state_file, apply=True)
            self.assertEqual(first["dashboard_writes"], 1)
            self.assertEqual(state_file.stat().st_mode & 0o777, 0o600)
            created_file = next(output_dir.glob("routerdhcp-*.json"))
            self.assertEqual(created_file.stat().st_mode & 0o777, 0o644)
            original = pages.load_state(state_file)
            second = pages.reconcile([event], {}, {"profiles": {}}, original,
                                     output_dir, state_file, apply=True)
            self.assertEqual(second["dashboard_writes"], 0)
            self.assertFalse(second["state_change"])

    def test_symlink_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as root:
            output = Path(root) / "dash.json"
            target = Path(root) / "target.json"
            target.write_text("protected")
            output.symlink_to(target)
            with self.assertRaises(ValueError):
                pages.atomic_json(output, {"x": 1}, apply=True)
            self.assertEqual(target.read_text(), "protected")

    def test_schema_failure_is_not_silently_reset(self):
        with tempfile.TemporaryDirectory() as root:
            file = Path(root) / "state.json"
            file.write_text(json.dumps({"schema_version": 2, "devices": {}}))
            with self.assertRaises(ValueError):
                pages.load_state(file)

    def test_loki_enforces_source_labels_and_event_limit(self):
        class Response:
            def __init__(self, obj):
                self.content = json.dumps(obj).encode()
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False
            def read(self, _):
                return self.content
        good = {"status": "success", "data": {"resultType": "streams",
                "result": [{"stream": {"host": "router-01", "service": "dnsmasq"},
                            "values": [["100", "DHCPACK(eth0) 192.168.2.101 " + MAC_A]]}]}}
        with patch.object(pages.urllib.request, "urlopen", return_value=Response(good)):
            found = pages.read_loki("http://127.0.0.1:3100", 200000)
        self.assertEqual(len(found), 1)
        good["data"]["result"][0]["stream"]["host"] = "other-host"
        with patch.object(pages.urllib.request, "urlopen", return_value=Response(good)):
            with self.assertRaises(ValueError):
                pages.read_loki("http://127.0.0.1:3100", 200000)


if __name__ == "__main__":
    unittest.main()
