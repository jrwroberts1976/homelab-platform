"""Unit tests for stable MAC-keyed Grafana dashboard generation."""
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = (Path(__file__).resolve().parents[2] /
          "ansible/roles/monitoring_stack/files/network-host-dashboard-generator.py")
spec = importlib.util.spec_from_file_location("network_host_dashboard_generator", SOURCE)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class GeneratorTests(unittest.TestCase):
    def test_valid_identifiers(self):
        self.assertTrue(generator.valid_key("mac:aa:bb:cc:dd:ee:ff"))
        self.assertTrue(generator.valid_key("ip:192.168.2.52"))
        self.assertFalse(generator.valid_key("ip:8.8.8.8"))
        self.assertFalse(generator.valid_key("mac:invalid"))
        key = "mac:aa:bb:cc:dd:ee:ff"
        self.assertEqual(generator.uid_for(key), generator.uid_for(key))
        self.assertTrue(generator.UID_RE.fullmatch(generator.uid_for(key)))

    def test_profile_is_constant_mac_link(self):
        original = {"uid": "homelab-mac-device-detail", "id": 123,
                    "templating": {"list": [
                        {"name": "host", "type": "query",
                         "query": "label_values(fake,hostname)"},
                        {"name": "device", "type": "query",
                         "query": "label_values(fake, device)"},
                        {"name": "node_host", "type": "query",
                         "query": "label_values(fake,hostname)"}
                    ]}}
        key = "mac:aa:bb:cc:dd:ee:ff"
        dashboard = generator.profile(original, key, {
            "hostname": "dns-01", "ip": "192.168.2.51"
        })
        self.assertEqual(dashboard["uid"], generator.uid_for(key))
        self.assertEqual(dashboard["templating"]["list"][0]["type"], "constant")
        self.assertEqual(dashboard["templating"]["list"][0]["current"]["value"], "dns-01")
        self.assertEqual(dashboard["templating"]["list"][0]["label"], "Host")
        self.assertEqual(dashboard["templating"]["list"][1]["current"]["value"], key)
        self.assertEqual(dashboard["templating"]["list"][1]["hide"], 2)
        self.assertEqual(dashboard["title"], "Homelab — dns-01")
        self.assertNotIn("aa:bb", dashboard["title"])
        self.assertEqual(original["templating"]["list"][0]["type"], "query")
        self.assertEqual(dashboard["id"], None)

    def test_dashboard_files_follow_mac_across_ip_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            template = root / "template.json"
            template.write_text(json.dumps({
                "uid": "homelab-mac-device-detail",
                "id": None,
                "templating": {"list": [
                    {"name": "host", "type": "query"},
                    {"name": "device", "type": "query"}
                ]}
            }))
            generated = root / "generated"
            cards = {}
            for i in range(10):
                key = "mac:aa:bb:cc:dd:ee:%02x" % i
                cards[key] = {
                    "device_key": key,
                    "dashboard_uid": generator.uid_for(key),
                    "hostname": "device-%s" % i,
                    "ip": "192.168.2.%d" % (50 + i)
                }
            with patch.object(generator, "TEMPLATE", template), \
                 patch.object(generator, "OUTPUT_DIR", generated), \
                 patch.object(generator, "query_cards", return_value=cards):
                generator.run()
                before = sorted(x.name for x in generated.glob("net-host-*.json"))
                self.assertEqual(len(before), 10)
                key = "mac:aa:bb:cc:dd:ee:00"
                cards[key]["ip"] = "192.168.2.225"
                cards[key]["hostname"] = "renamed-host"
                generator.run()
                after = sorted(x.name for x in generated.glob("net-host-*.json"))
                self.assertEqual(before, after)
                record = json.loads(
                    (generated / (generator.uid_for(key) + ".json")).read_text())
                self.assertEqual(record["title"], "Homelab — renamed-host")
                self.assertEqual(record["templating"]["list"][0]["current"]["value"],
                                 "renamed-host")
                self.assertEqual(record["uid"], generator.uid_for(key))

    def test_unnamed_device_uses_ip_instead_of_mac(self):
        key = "mac:de:ad:be:ef:00:01"
        template = {
            "uid": "homelab-mac-device-detail",
            "templating": {"list": [
                {"name": "host"},
                {"name": "device"}
            ]}
        }
        dashboard = generator.profile(template, key, {
            "hostname": "", "ip": "192.168.2.224"
        })
        self.assertEqual(dashboard["title"], "Homelab — 192.168.2.224")
        self.assertNotIn("de:ad", dashboard["title"])
        self.assertEqual(dashboard["templating"]["list"][0]["current"]["text"],
                         "192.168.2.224")

    def test_generator_refuses_partial_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "template.json").write_text(json.dumps({
                "uid": "homelab-mac-device-detail",
                "templating": {"list": [{"name": "device"}]}}))
            with patch.object(generator, "TEMPLATE", root / "template.json"), \
                 patch.object(generator, "OUTPUT_DIR", root / "generated"), \
                 patch.object(generator, "query_cards", return_value={
                    "mac:aa:bb:cc:dd:ee:ff": {"hostname": "only-one"}}):
                # Mocked query bypasses query_cards's own 10-device guard;
                # run's prior-output drop protection still applies.
                (root / "generated").mkdir()
                for i in range(10):
                    (root / "generated" / ("net-host-%012x.json" % i)).write_text("{}")
                with self.assertRaises(ValueError):
                    generator.run()

    def test_router_profile_contains_only_recorded_network_panels(self):
        template_path = (Path(__file__).resolve().parents[2] /
                         "ansible/roles/monitoring_stack/files/host-profile-template.json")
        template = json.loads(template_path.read_text())
        self.assertGreaterEqual(len(template["panels"]), 20)
        key = "mac:aa:bb:cc:dd:ee:ff"
        metric = {
            "hostname": "ASUS router", "ip": "192.168.2.1",
            "status": "Online", "dns_hint": ""
        }
        availability = (
            {name: set() for name in generator.AVAILABILITY_QUERIES},
            {key}, {key}, {key}
        )
        profile = generator.profile(template, key, metric, availability)
        chosen = {p["id"] for p in profile["panels"]}
        self.assertEqual(chosen, {9, 10, 11, 14, 15, 17})
        self.assertEqual([p["gridPos"]["y"] for p in profile["panels"][:3]],
                         [0, 0, 0])
        self.assertNotIn("No telemetry", json.dumps(profile))
        self.assertTrue(all(p["type"] != "text" for p in profile["panels"]))
        self.assertTrue(all(p["gridPos"]["y"] <= 30 for p in profile["panels"]))

    def test_linux_profile_includes_only_available_telemetry(self):
        template_path = (Path(__file__).resolve().parents[2] /
                         "ansible/roles/monitoring_stack/files/host-profile-template.json")
        template = json.loads(template_path.read_text())
        key = "mac:aa:bb:cc:dd:ee:ab"
        metric = {
            "hostname": "sensor-01", "ip": "192.168.2.55",
            "status": "Online", "dns_hint": ""
        }
        metrics = {name: set() for name in generator.AVAILABILITY_QUERIES}
        for category in ("cpu", "memory", "memory_total", "network",
                         "filesystem", "filesystem_size", "updates",
                         "security_updates", "load"):
            metrics[category].add("sensor-01")
        available = (metrics, set(), {key}, {key})
        chosen = generator.select_panel_ids(key, metric, available)
        self.assertIn(1, chosen)
        self.assertIn(2, chosen)
        self.assertIn(3, chosen)  # A recorded zero is still valid data.
        self.assertIn(4, chosen)
        self.assertIn(5, chosen)
        self.assertIn(7, chosen)
        self.assertIn(8, chosen)
        self.assertNotIn(11, chosen)
        self.assertNotIn(15, chosen)
        self.assertNotIn(16, chosen)
        self.assertNotIn(18, chosen)
        self.assertNotIn(21, chosen)
        panels = generator.compact_panels(template["panels"], chosen)
        self.assertEqual(len(panels), len(chosen))
        self.assertTrue(all(p["gridPos"]["x"] + p["gridPos"]["w"] <= 24
                            for p in panels))
        self.assertEqual(
            max(p["gridPos"]["y"] + p["gridPos"]["h"] for p in panels),
            sum(max(p["gridPos"]["h"] for p in panels if p["gridPos"]["y"] == y)
                for y in sorted({p["gridPos"]["y"] for p in panels}))
        )

    def test_no_observed_ports_does_not_make_fake_zero_panel(self):
        key = "ip:192.168.2.206"
        metrics = {name: set() for name in generator.AVAILABILITY_QUERIES}
        chosen = generator.select_panel_ids(
            key, {"hostname": "phone", "status": "Online",
                  "dns_hint": "Google ecosystem activity"},
            (metrics, set(), set(), {key}))
        self.assertEqual(chosen, {9, 14, 16, 17})

    def test_query_rejects_too_few_devices(self):
        data = {"status": "success", "data": {"result": [{
            "metric": {
                "device_key": "mac:aa:bb:cc:dd:ee:ff",
                "dashboard_uid": generator.uid_for(
                    "mac:aa:bb:cc:dd:ee:ff")}
        }]}}
        with patch.object(generator, "urlopen",
                          return_value=io.BytesIO(json.dumps(data).encode())):
            with self.assertRaises(ValueError):
                generator.query_cards()


if __name__ == "__main__":
    unittest.main()
