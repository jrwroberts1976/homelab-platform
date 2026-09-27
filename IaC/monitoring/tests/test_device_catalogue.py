"""Device catalogue is generated only from evidence and preserves operator notes."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "IaC/monitoring/audits/build_device_catalogue.py"
spec = importlib.util.spec_from_file_location("build_device_catalogue", SCRIPT)
catalogue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalogue)


class DeviceCatalogueTests(unittest.TestCase):
    def test_generate_pages_without_overwriting_notes(self):
        with tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp)
            (evidence / "network-scan.json").write_text(json.dumps({
                "scan_time": "2026-09-27T12:00:00+01:00",
                "scan_source": "monitor-01/192.168.2.52",
                "hosts": [
                    {"ip": "192.168.2.52", "mac": "02:00:00:00:02:52",
                     "names": [], "open_ports": [{"port": 9090, "protocol": "tcp",
                                                 "service": "http", "product": "Prometheus",
                                                 "version": "v1"}]},
                    {"ip": "192.168.2.199", "mac": "02:00:00:00:02:99",
                     "names": [], "open_ports": []}
                ]}))
            directory, count, _ = catalogue.build(evidence, ROOT)
            self.assertEqual(count, 2)
            self.assertTrue((directory / "devices/monitor-01.md").exists())
            unknown = directory / "devices/mac-02-00-00-00-02-99.md"
            self.assertTrue(unknown.exists())
            notes = directory / "notes/monitor-01.md"
            notes.write_text("Important custom notes\n")
            directory2, count2, _ = catalogue.build(evidence, ROOT)
            self.assertEqual(directory2, directory)
            self.assertEqual(count2, 2)
            self.assertEqual(notes.read_text(), "Important custom notes\n")
            self.assertIn("9090/tcp", (directory / "devices/monitor-01.md").read_text())
            self.assertIn("Unverified", unknown.read_text())

    def test_invalid_identifiers_rejected(self):
        with self.assertRaises(ValueError):
            catalogue.safe_slug("!")


if __name__ == "__main__":
    unittest.main()
