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
        self.assertEqual(dashboard["templating"]["list"][0]["current"]["value"], key)
        self.assertEqual(original["templating"]["list"][0]["type"], "query")
        self.assertEqual(dashboard["id"], None)

    def test_dashboard_files_follow_mac_across_ip_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            template = root / "template.json"
            template.write_text(json.dumps({
                "uid": "homelab-mac-device-detail",
                "id": None,
                "templating": {"list": [{"name": "device", "type": "query"}]}
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
                self.assertIn("renamed-host", record["title"])
                self.assertEqual(record["uid"], generator.uid_for(key))

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
