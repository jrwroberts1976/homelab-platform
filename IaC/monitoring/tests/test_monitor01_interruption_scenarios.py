"""Isolated *simulation* of Gate 3 failure boundaries.

Uses synthetic files and timer/notification state in TemporaryDirectory;
never contacts hosts, runs Ansible, starts systemd or sends email.
The transition constraints are compared to the actual playbook structure
by the separate test_monitor01_* guard tests. This simulation is not
a substitute for interrupted Ansible execution in a disposable VM pair.
"""
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import tempfile
import unittest


NAMES = ("inventory.json", "deep-profiles.json", "enrichment.json",
         "alerted-macs.json", "alerts.env")
OLD_TIMERS = {"collector": True, "enricher": True, "deep": False,
              "os_evidence": True}
NEW_TIMERS = {"collector": False, "enricher": False, "deep": False,
              "os_evidence": False, "guest_refresh": False}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class Lab:
    root: Path
    source: Path = field(init=False)
    target: Path = field(init=False)
    backup: Path = field(init=False)
    frozen_hashes: dict = field(default_factory=dict)
    source_timers: dict = field(default_factory=lambda: OLD_TIMERS.copy())
    target_timers: dict = field(default_factory=lambda: NEW_TIMERS.copy())
    target_marker: bool = False
    notifier_wired: bool = False
    target_collector_ever_ran: bool = False
    target_notifier_ever_ran: bool = False

    def __post_init__(self):
        self.source = self.root / "source"
        self.target = self.root / "target"
        self.backup = self.root / "target_backup"
        self.source.mkdir()
        self.target.mkdir()
        fixtures = {
            "inventory.json": {"192.0.2.10": {"mac": "02:00:00:00:00:01",
                                               "online": True}},
            "deep-profiles.json": {"profiles": {}},
            "enrichment.json": {"hosts": {}},
            "alerted-macs.json": {
                "version": 1,
                "devices": {
                    "02:00:00:00:00:01": {"status": "baseline"},
                    "02:00:00:00:00:ff": {"status": "alerted"},
                }},
            "alerts.env": "NETWORK_DEVICE_ALERT_TO=example@invalid.test\n",
        }
        for name, value in fixtures.items():
            (self.source / name).write_text(
                value if isinstance(value, str) else json.dumps(value))
        for name in NAMES[:3]:
            (self.target / name).write_bytes((self.source / name).read_bytes())
        (self.target / "proxmox-guests.json").write_text('{"guests":{}}')

    def freeze(self):
        assert any(self.source_timers.values())
        assert not any(self.target_timers.values())
        self.source_timers = {name: False for name in self.source_timers}
        self.frozen_hashes = {name: sha(self.source / name) for name in NAMES}

    def copy_prefix(self, count):
        assert self.frozen_hashes and not any(self.source_timers.values())
        if count:
            self.backup.mkdir(exist_ok=True)
            for name in (*NAMES[:3], "proxmox-guests.json"):
                (self.backup / name).write_bytes((self.target / name).read_bytes())
        for name in NAMES[:count]:
            (self.target / name).write_bytes((self.source / name).read_bytes())

    def can_recover_pre_activation(self):
        return (bool(self.frozen_hashes)
                and not any(self.source_timers.values())
                and not any(self.target_timers.values())
                and not self.target_marker and not self.notifier_wired
                and not self.target_collector_ever_ran
                and not self.target_notifier_ever_ran
                and all((self.source / name).exists()
                        and sha(self.source / name) == expected
                        for name, expected in self.frozen_hashes.items()))

    def recover_pre_activation(self):
        if not self.can_recover_pre_activation():
            return False
        self.source_timers = OLD_TIMERS.copy()
        return True

    def can_activate(self):
        return (bool(self.frozen_hashes)
                and not any(self.source_timers.values())
                and not any(self.target_timers.values())
                and all((self.target / name).exists()
                        and sha(self.target / name) == expected
                        for name, expected in self.frozen_hashes.items())
                and self.backup.is_dir())

    def activate(self):
        if not self.can_activate():
            return False
        self.notifier_wired = True
        self.target_marker = True
        self.target_timers.update(collector=True, enricher=True,
                                  guest_refresh=True, os_evidence=True)
        self.target_collector_ever_ran = True
        self.target_notifier_ever_ran = True
        return True

    def can_rollback_after_activation(self):
        return (not any(self.target_timers.values())
                and (self.target / "alerted-macs.json").exists()
                and sha(self.target / "alerted-macs.json")
                    == self.frozen_hashes["alerted-macs.json"])

    def rollback_after_activation(self):
        if not self.can_rollback_after_activation():
            return False
        self.target_marker = False
        self.source_timers = OLD_TIMERS.copy()
        return True


class InterruptedCutoverScenarios(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.lab = Lab(Path(self.temp.name))

    def test_freeze_without_transfer_can_restore_original_source(self):
        self.lab.freeze()
        self.assertTrue(self.lab.recover_pre_activation())
        self.assertEqual(self.lab.source_timers, OLD_TIMERS)
        self.assertFalse(self.lab.target_marker)

    def test_each_partial_transfer_prefix_can_restore_without_target_alert_registry(self):
        for count in range(len(NAMES)):
            with self.subTest(files_copied=count):
                with tempfile.TemporaryDirectory() as directory:
                    lab = Lab(Path(directory))
                    lab.freeze()
                    lab.copy_prefix(count)
                    before = {p.name: sha(p) for p in lab.target.iterdir()
                              if p.is_file()}
                    self.assertTrue(lab.recover_pre_activation())
                    self.assertEqual(lab.source_timers, OLD_TIMERS)
                    self.assertEqual(
                        before, {p.name: sha(p) for p in lab.target.iterdir()
                                 if p.is_file()})

    def test_partial_copy_cannot_activate(self):
        self.lab.freeze()
        self.lab.copy_prefix(3)
        self.assertFalse(self.lab.activate())
        self.assertFalse(self.lab.target_marker)

    def test_full_copy_with_all_five_hashes_can_activate_without_deep(self):
        self.lab.freeze()
        self.lab.copy_prefix(5)
        self.assertTrue(self.lab.activate())
        self.assertFalse(self.lab.target_timers["deep"])
        self.assertFalse(any(self.lab.source_timers.values()))

    def test_corrupt_transferred_registry_refuses_activation(self):
        self.lab.freeze()
        self.lab.copy_prefix(5)
        (self.lab.target / "alerted-macs.json").write_text('{"devices":{}}')
        self.assertFalse(self.lab.activate())

    def test_corrupt_frozen_source_refuses_pre_activation_recovery(self):
        self.lab.freeze()
        (self.lab.source / "alerted-macs.json").write_text('{"devices":{}}')
        self.assertFalse(self.lab.recover_pre_activation())

    def test_partial_activation_marker_or_notifier_wiring_refuses_early_recovery(self):
        self.lab.freeze()
        self.lab.copy_prefix(5)
        self.lab.target_marker = True
        self.assertFalse(self.lab.recover_pre_activation())
        self.lab.target_marker = False
        self.lab.notifier_wired = True
        self.assertFalse(self.lab.recover_pre_activation())

    def test_post_activation_new_notification_blocks_automatic_source_revival(self):
        self.lab.freeze()
        self.lab.copy_prefix(5)
        self.assertTrue(self.lab.activate())
        registry = json.loads((self.lab.target / "alerted-macs.json").read_text())
        registry["devices"]["02:00:00:00:00:02"] = {"status": "alerted"}
        (self.lab.target / "alerted-macs.json").write_text(json.dumps(registry))
        self.lab.target_timers = {name: False for name in self.lab.target_timers}
        self.assertFalse(self.lab.rollback_after_activation())
        self.assertFalse(any(self.lab.source_timers.values()))

    def test_no_alert_delta_allows_source_after_stopping_destination(self):
        self.lab.freeze()
        self.lab.copy_prefix(5)
        self.assertTrue(self.lab.activate())
        self.assertFalse(self.lab.rollback_after_activation())
        self.lab.target_timers = {name: False for name in self.lab.target_timers}
        self.assertTrue(self.lab.rollback_after_activation())
        self.assertEqual(self.lab.source_timers, OLD_TIMERS)


if __name__ == "__main__":
    unittest.main()
