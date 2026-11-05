"""Offline regression checks for targeted Grafana panel-30 update."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/router01_hosts_panel30_patch.py"
spec = importlib.util.spec_from_file_location("panel30_patch", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class DashboardPanelPatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        stage = root / "stage"
        stage.mkdir(mode=0o700)
        live = root / "live.json"
        self.patches = [
            patch.object(mod, "STAGE", stage),
            patch.object(mod, "LIVE", live),
            patch.object(mod, "BACKUP", stage / "grafana-hosts-before-panel30.json"),
            patch.object(mod, "DEPLOYED_HASH", stage / "grafana-hosts-after-panel30.sha256"),
        ]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)
        self.original = {
            "uid": "homelab-linux-estate",
            "panels": [
                {"id": 29, "targets": [{"expr": 'node_os_info{job="router-node-exporter",target_name="$host"} or another_query'}]},
                {"id": 30, "targets": [{"expr": mod.OLD}]},
                {"id": 31, "targets": [{"expr": "unchanged"}]},
            ],
        }
        live.write_text(json.dumps(self.original))

    def run_mode(self, mode):
        with patch.object(sys, "argv", ["panel30_patch.py", mode]):
            mod.main()

    def test_apply_preserves_every_other_panel_and_rollback(self):
        self.run_mode("preflight")
        self.run_mode("apply")
        updated = json.loads(mod.LIVE.read_text())
        self.assertEqual(updated["panels"][0], self.original["panels"][0])
        self.assertEqual(updated["panels"][2], self.original["panels"][2])
        self.assertEqual(updated["panels"][1]["targets"][0]["expr"], mod.NEW)
        self.run_mode("verify")
        self.run_mode("rollback")
        self.assertEqual(json.loads(mod.LIVE.read_text()), self.original)

    def test_refuses_missing_os_fallback(self):
        data = json.loads(mod.LIVE.read_text())
        data["panels"][0]["targets"][0]["expr"] = "old_unqualified_os_metric"
        mod.LIVE.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            self.run_mode("preflight")

    def test_refuses_unknown_panel30_state(self):
        data = json.loads(mod.LIVE.read_text())
        data["panels"][1]["targets"][0]["expr"] = "unrecognised"
        mod.LIVE.write_text(json.dumps(data))
        with self.assertRaises(SystemExit):
            self.run_mode("apply")

    def test_rollback_rejects_intervening_dashboard_change(self):
        self.run_mode("apply")
        data = json.loads(mod.LIVE.read_text())
        data["panels"][2]["targets"][0]["expr"] = "subsequent_edit"
        mod.LIVE.write_text(json.dumps(data))
        with self.assertRaises(SystemExit):
            self.run_mode("rollback")


if __name__ == "__main__":
    unittest.main()
