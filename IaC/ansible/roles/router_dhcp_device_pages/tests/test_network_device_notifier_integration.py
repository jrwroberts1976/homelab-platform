"""Render the existing Ansible notifier and test no-send DHCP integration offline."""
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from jinja2 import Environment

HERE = Path(__file__).resolve().parents[1]
TEMPLATE = HERE.parent / "network_host_collector" / "templates" / "homelab-network-device-email-alert.py.j2"
# The real network_host_collector role is a sibling to router_dhcp_device_pages.
TEMPLATE = HERE.parents[0] / "network_host_collector" / "templates" / "homelab-network-device-email-alert.py.j2"
FILES = HERE / "files"
MAC = "02:11:22:33:44:55"
TIME = 1_800_000_000_000_000_000


def rendered_source():
    env = Environment(autoescape=False)
    env.filters["to_json"] = json.dumps
    return env.from_string(TEMPLATE.read_text()).render(
        network_host_collector_inventory="/tmp/unused-inventory.json",
        network_host_collector_alert_registry="/tmp/unused-registry.json",
        network_host_collector_alert_smtp_host="127.0.0.1",
        network_host_collector_alert_smtp_port=25,
        network_host_collector_alert_from="test@localhost",
        network_host_collector_expected_hostname="monitor-01",
    )


def notifier_module():
    source = rendered_source()
    compile(source, str(TEMPLATE), "exec")
    namespace = {"__name__": "test_notifier"}
    exec(source, namespace)
    return namespace


class NotifierIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.module = notifier_module()
        self.inventory = self.root / "inventory.json"
        self.registry = self.root / "alerted-macs.json"
        self.marker = self.root / "activated.json"
        self.dhcp = self.root / "dhcp-state.json"
        self.profiles = self.root / "profiles.json"
        self.pages = self.root / "pages"
        self.pages.mkdir()
        self.module.update({
            "INVENTORY_FILE": self.inventory,
            "REGISTRY_FILE": self.registry,
            "DHCP_EMAIL_MARKER": self.marker,
            "DHCP_DEVICE_STATE": self.dhcp,
            "DHCP_NMAP_PROFILES": self.profiles,
            "DHCP_DASHBOARD_DIR": self.pages,
            "DHCP_POLICY_LIB": str(FILES),
            "MAIL_TO": "test@localhost",
        })

    def test_rendered_notifier_is_valid_python(self):
        self.assertIn("DHCP_EMAIL_MARKER", rendered_source())
        self.assertIn("network_device_alert_sent", rendered_source())

    def test_message_adds_router_grafana_url_and_inferred_os(self):
        msg = self.module["build_device_message"]({
            "mac": MAC, "ip": "192.168.2.101", "hostname": "new-device",
            "source": "router-01 DHCPACK",
            "os_evidence": "Nmap inferred: Linux (match score 95%)",
            "dashboard_url": "https://grafana.home.jrwroberts.co.uk/d/routerdhcp-test",
        })
        content = msg.get_content()
        self.assertIn("router-01 DHCPACK", content)
        self.assertIn("Nmap inferred:", content)
        self.assertIn("/d/routerdhcp-test", content)

    def test_no_marker_keeps_original_send_free_preview(self):
        self.inventory.write_text(json.dumps({"192.168.2.101": {
            "mac": MAC, "online": True, "hostname": "new-device"}}))
        self.registry.write_text(json.dumps({"version": 1, "devices": {}}))
        before = self.registry.read_bytes()
        with patch.object(sys, "argv", ["notifier", "--preview"]), \
             patch.dict(self.module, {"send_message": lambda msg: (_ for _ in ()).throw(
                 AssertionError("Preview sent an email"))}), redirect_stdout(io.StringIO()) as output:
            rc = self.module["main"]()
        self.assertEqual(rc, 0)
        self.assertEqual(self.registry.read_bytes(), before)
        self.assertIn('"email_sent":false', output.getvalue())

    def test_new_dhcp_page_uses_shared_ledger_and_only_one_sender(self):
        self.inventory.write_text("{}")
        self.registry.write_text(json.dumps({"version": 1, "devices": {}}))
        self.marker.write_text(json.dumps(
            {"schema_version": 1, "activated_at_ns": TIME}))
        self.dhcp.write_text(json.dumps({"schema_version": 1, "devices": {
            MAC: {"ip": "192.168.2.101", "hostname": "tablet",
                  "first_seen_ns": TIME + 1000000000,
                  "last_seen_ns": TIME + 2000000000}}}))
        self.profiles.write_text(json.dumps({"profiles": {
            MAC: {"profiled_ip": "192.168.2.101",
                  "profile": {"tcp": {"os_matches": [{"name": "Android",
                                                    "accuracy": "90"}]}}}}}))
        import hashlib
        uid = "routerdhcp-" + hashlib.sha256(MAC.encode("ascii")).hexdigest()[:20]
        (self.pages / (uid + ".json")).write_text(json.dumps({"uid": uid}))
        sent = []
        with patch.object(sys, "argv", ["notifier"]), \
             patch("time.time_ns", return_value=TIME + 4_000_000_000), \
             patch.dict(self.module, {"send_message": lambda msg: sent.append(msg)}), \
             redirect_stdout(io.StringIO()):
            self.assertEqual(self.module["main"](), 0)
            self.assertEqual(self.module["main"](), 0)
        self.assertEqual(len(sent), 1)
        self.assertIn("Android", sent[0].get_content())
        self.assertIn("/d/" + uid, sent[0].get_content())
        self.assertIn(MAC, json.loads(self.registry.read_text())["devices"])

    def test_each_successful_smtp_is_persisted_before_next_error(self):
        second = "02:11:22:33:44:66"
        inv = {"192.168.2.101": {"mac": MAC, "online": True},
               "192.168.2.102": {"mac": second, "online": True}}
        self.inventory.write_text(json.dumps(inv))
        self.registry.write_text(json.dumps({"version": 1, "devices": {}}))
        attempts = []
        def sender(msg):
            attempts.append(msg)
            if len(attempts) == 2:
                raise RuntimeError("SMTP failed for second host")
        with patch.object(sys, "argv", ["notifier"]), \
             patch.dict(self.module, {"send_message": sender}), \
             redirect_stdout(io.StringIO()):
            self.assertEqual(self.module["main"](), 0)
        known = json.loads(self.registry.read_text())["devices"]
        self.assertIn(MAC, known)
        self.assertNotIn(second, known)


if __name__ == "__main__":
    unittest.main()
