"""Offline safety tests: approval separation, protected history and rollback boundaries."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import yaml

ROOT = Path(__file__).resolve().parents[2] / "ansible"
PLAYBOOKS = ROOT / "playbooks"
GUARD_PATH = ROOT / "roles/network_host_collector/files/homelab-network-firstseen-guard.py"
DROPIN = ROOT / "roles/network_host_collector/files/30-network-cutover-firstseen.conf"


def playbook(name):
    return yaml.safe_load((PLAYBOOKS / f"network-host-monitor01-{name}.yml").read_text())


class Gate3PhaseContractTests(unittest.TestCase):
    def test_phases_have_independent_explicit_production_approval(self):
        for name, token in (
            ("gate3b-source-freeze", "APPROVE-STOP-PROXMOX-2-NETWORK-DISCOVERY"),
            ("gate3c-final-sync", "APPROVE-FINAL-PROTECTED-NETWORK-DELTA-SYNC"),
            ("gate3d-activate", "APPROVE-MONITOR-01-NETWORK-DISCOVERY-ACTIVATION"),
            ("gate3e-preactivation-rollback", "APPROVE-PREACTIVATION-RETURN-TO-PROXMOX-2"),
        ):
            with self.subTest(phase=name):
                raw = (PLAYBOOKS / f"network-host-monitor01-{name}.yml").read_text()
                self.assertIn(token, raw)
                self.assertIn("ansible.builtin.assert", raw)

    def test_freeze_records_original_timer_states_before_disabling(self):
        phase = playbook("gate3b-source-freeze")
        self.assertEqual(phase[0]["import_playbook"], "network-host-monitor01-cutover-preflight.yml")
        self.assertEqual(phase[1]["hosts"], "Proxmox-2")
        steps = phase[1]["tasks"]
        names = [s["name"] for s in steps]
        self.assertLess(
            names.index("Preserve the four original source timer states before any disablement"),
            names.index("Disable and stop ONLY four legacy network discovery timers"),
        )
        self.assertLess(
            names.index("Wait for existing collector, enrichment, profiler and publisher oneshots to finish normally"),
            names.index("Write final root-only frozen marker only after all source workers drained"),
        )

    def test_sync_backup_first_and_no_service_start(self):
        phase = playbook("gate3c-final-sync")
        self.assertEqual([p["hosts"] for p in phase], ["Proxmox-2", "monitoring_hosts"])
        source = [x["name"] for x in phase[0]["tasks"]]
        self.assertLess(
            source.index("Make a new root-only final source backup directory"),
            source.index("Read exactly five protected frozen files over authenticated Ansible transport"),
        )
        target = [x["name"] for x in phase[1]["tasks"]]
        self.assertLess(
            target.index("Backup all four pre-existing protected target JSON files"),
            target.index("Copy EXACT frozen source evidence bytes and historical MAC registry"),
        )
        self.assertLess(
            target.index("Preserve a separate root-only copy of the complete frozen alert registry for activation and rollback"),
            target.index("Save root-only post-sync readiness and rollback manifest without activating any service"),
        )
        code = str(phase)
        self.assertNotIn("ansible.builtin.systemd_service", code)
        self.assertNotIn("--test-email", code)
        for stage in phase:
            for task in stage["tasks"]:
                if "ansible.builtin.slurp" in task or "ansible.builtin.copy" in task and "content" in task["ansible.builtin.copy"]:
                    self.assertTrue(task.get("no_log"), task["name"])

    def test_activation_keeps_deep_profile_opt_in(self):
        phase = playbook("gate3d-activate")
        self.assertEqual([p["hosts"] for p in phase], ["Proxmox-2", "monitoring_hosts"])
        target = phase[1]["tasks"]
        names = [t["name"] for t in target]
        self.assertLess(
            names.index("Reconfirm the source collector/enricher/profiler/publisher never resumed before target activation"),
            names.index("Run exactly one explicitly approved target collector cycle with the original first-seen registry"),
        )
        self.assertLess(
            names.index("Verify full historical registry and zero pending online alerts after first production target scan"),
            names.index("Enable ONLY the reviewed target network collector timer"),
        )
        self.assertIn("Require expensive deep profiler stays disabled until a later explicit decision", names)
        self.assertNotIn(
            "homelab-network-host-deep-profiler.timer\n        state: started",
            (PLAYBOOKS / "network-host-monitor01-gate3d-activate.yml").read_text(),
        )

    def test_early_rollback_refuses_any_postactivation_state(self):
        phase = playbook("gate3e-preactivation-rollback")
        self.assertEqual([p["hosts"] for p in phase], ["monitoring_hosts", "Proxmox-2"])
        source = [x["name"] for x in phase[1]["tasks"]]
        self.assertLess(
            source.index("Save root-only rollback intent before re-enabling any source timer"),
            source.index("Restore exact original enablement and active state of each network-only timer"),
        )
        raw = (PLAYBOOKS / "network-host-monitor01-gate3e-preactivation-rollback.yml").read_text()
        self.assertIn("not item.stat.exists", raw)
        self.assertIn("30-network-cutover-firstseen.conf", raw)
        self.assertIn("final/alerted-macs.json", raw)

    def test_systemd_collector_requires_approval_and_guard(self):
        conf = DROPIN.read_text()
        self.assertIn("ConditionPathExists=/etc/homelab-network-hosts/network-discovery-cutover-approved", conf)
        self.assertIn("EnvironmentFile=/etc/homelab-network-hosts/alerts.env", conf)
        self.assertIn("ExecStartPre=/usr/local/sbin/homelab-network-firstseen-guard", conf)
        self.assertIn("ExecStartPost=-/usr/local/sbin/homelab-network-device-email-alert", conf)


class FrozenAlertHistoryGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.state = base / "state"
        self.config = base / "config"
        self.backup_root = base / "backups"
        self.state.mkdir()
        self.config.mkdir()
        self.backup_root.mkdir()
        self.run_id = "20260927T080000"
        self.backup = self.backup_root / ("gate3-target-" + self.run_id)
        self.backup.mkdir()
        self.original = {
            "version": 1,
            "devices": {
                "aa:00:00:00:00:01": {"status": "alerted"},
                "aa:00:00:00:00:02": {"status": "baseline"},
            },
        }
        self.write(self.backup / "final-alerted-macs.json", self.original)
        self.write(self.state / "alerted-macs.json", self.original)
        self.write(self.config / "alerts.env", "NETWORK_DEVICE_ALERT_TO=private@example.invalid\n")
        self.manifest = {
            "schema_version": 1,
            "event": "network_discovery_final_sync_complete",
            "run_id": self.run_id,
            "target_host": "monitor-01",
            "target_backup_dir": str(self.backup),
            "historical_registry_count": 2,
            "sha256": ["0"] * 5,
        }
        self.manifest["sha256"][3] = hashlib.sha256(
            (self.backup / "final-alerted-macs.json").read_bytes()
        ).hexdigest()
        self.write(self.state / "network-discovery-final-sync.json", self.manifest)
        self.write(
            self.config / "network-discovery-cutover-approved",
            {"event": "network_discovery_cutover_approved", "run_id": self.run_id},
        )

        spec = importlib.util.spec_from_file_location("firstseen_guard_under_test", GUARD_PATH)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.STATE = self.state
        mod.CONFIG = self.config
        mod.SYNC = self.state / "network-discovery-final-sync.json"
        mod.APPROVAL = self.config / "network-discovery-cutover-approved"
        mod.REGISTRY = self.state / "alerted-macs.json"
        mod.ALERT_ENV = self.config / "alerts.env"
        mod.BACKUP_ROOT = self.backup_root
        mod.protected = lambda path: path.read_bytes()
        self.guard = mod

    @staticmethod
    def write(path, data):
        path.write_text(
            json.dumps(data, sort_keys=True) if isinstance(data, dict) else data
        )

    def check(self):
        with mock.patch.object(self.guard.os, "geteuid", return_value=0):
            self.guard.main()

    def test_valid_original_history(self):
        self.check()

    def test_new_alert_added_preserves_old_alert_and_baseline(self):
        current = json.loads((self.state / "alerted-macs.json").read_text())
        current["devices"]["aa:00:00:00:00:03"] = {"status": "alerted"}
        self.write(self.state / "alerted-macs.json", current)
        self.check()

    def test_refuses_missing_historical_mac_even_when_count_is_unchanged(self):
        current = json.loads((self.state / "alerted-macs.json").read_text())
        del current["devices"]["aa:00:00:00:00:02"]
        current["devices"]["aa:00:00:00:00:03"] = {"status": "alerted"}
        self.write(self.state / "alerted-macs.json", current)
        with self.assertRaisesRegex(ValueError, "historical"):
            self.check()

    def test_refuses_downgrade_of_previously_alerted_mac(self):
        current = json.loads((self.state / "alerted-macs.json").read_text())
        current["devices"]["aa:00:00:00:00:01"]["status"] = "baseline"
        self.write(self.state / "alerted-macs.json", current)
        with self.assertRaisesRegex(ValueError, "delivery state"):
            self.check()

    def test_refuses_changed_original_backup(self):
        current = json.loads((self.backup / "final-alerted-macs.json").read_text())
        current["devices"]["aa:00:00:00:00:02"]["status"] = "alerted"
        self.write(self.backup / "final-alerted-macs.json", current)
        with self.assertRaisesRegex(ValueError, "match source"):
            self.check()

    def test_refuses_missing_approval(self):
        (self.config / "network-discovery-cutover-approved").unlink()
        with self.assertRaises(FileNotFoundError):
            self.check()

    def test_refuses_missing_recipient(self):
        self.write(self.config / "alerts.env", "# intentionally no recipient\n")
        with self.assertRaisesRegex(ValueError, "recipient"):
            self.check()

    def test_refuses_unknown_run_id(self):
        marker = self.config / "network-discovery-cutover-approved"
        self.write(marker, {"event": "network_discovery_cutover_approved", "run_id": "WRONG"})
        with self.assertRaisesRegex(ValueError, "matching"):
            self.check()


if __name__ == "__main__":
    unittest.main()
