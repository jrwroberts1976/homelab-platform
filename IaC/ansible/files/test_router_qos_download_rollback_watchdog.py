#!/usr/bin/env python3
"""Offline real-shell tests of file-only rollback, no router/root/network access."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).with_name("router-qos-download-rollback-watchdog.sh")

class WatchdogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.store = self.root / "backups"
        self.store.mkdir()
        self.active = self.root / "live"
        self.active.mkdir()
        self.old_ctrl = b"legacy-controller-content\n"
        self.old_hook = b"legacy-hook-content\n"
        (self.store / "legacy-controller").write_bytes(self.old_ctrl)
        (self.store / "legacy-ip-up-hook").write_bytes(self.old_hook)
        self.ctrl = self.active / "controller"
        self.hook = self.active / "ip-up"
        self.ctrl.write_text("candidate\n")
        self.hook.write_text("candidate\n")
        script = SOURCE.read_text()
        replacements = {
            '[[ $EUID -eq 0 && "$(hostname -s)" == raspberrypi ]] || exit 2': 'true',
            'ROOT=/var/lib/router-qos-download-cutover': 'ROOT=' + str(self.store),
            'ACTIVE_CTRL=/usr/local/sbin/router-qos-download-basic': 'ACTIVE_CTRL=' + str(self.ctrl),
            'ACTIVE_HOOK=/etc/ppp/ip-up.d/router-qos-download': 'ACTIVE_HOOK=' + str(self.hook),
            'OLD_CTRL=16f7db14bf5962360e7c684e374c7d676240f78ea1351effc66472031f0486a7':
                'OLD_CTRL=' + hashlib.sha256(self.old_ctrl).hexdigest(),
            'OLD_HOOK=25b96d3504f226a789cc959772a995e51e2867ecc797c3e218c3b6d89b75df8b':
                'OLD_HOOK=' + hashlib.sha256(self.old_hook).hexdigest(),
            'LOCK=/run/lock/router-qos-download-basic.lock': 'LOCK=' + str(self.root / "lock"),
            'mktemp /usr/local/sbin/.router-qos-rollback.XXXXXX': 'mktemp ' + str(self.active / ".controller.XXXXXX"),
            'mktemp /etc/ppp/ip-up.d/.router-qos-rollback.XXXXXX': 'mktemp ' + str(self.active / ".hook.XXXXXX"),
            'chown root:root "$ctmp" "$htmp"': 'true # user-namespace simulation; production chown remains intact',
        }
        for old, new in replacements.items():
            self.assertIn(old, script)
            script = script.replace(old, new)
        self.script = self.root / "test-watchdog.sh"
        self.script.write_text(script)

    def run_watchdog(self, mode):
        return subprocess.run(["bash", str(self.script), mode],
                              capture_output=True, text=True, timeout=10)

    def test_valid_backup_verify_is_read_only(self):
        result = self.run_watchdog("verify")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.ctrl.read_text(), "candidate\n")
        self.assertEqual(self.hook.read_text(), "candidate\n")

    def test_restore_both_entrypoints(self):
        result = self.run_watchdog("restore")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "", "EXIT trap must not reference out-of-scope paths")
        self.assertEqual(self.ctrl.read_bytes(), self.old_ctrl)
        self.assertEqual(self.hook.read_bytes(), self.old_hook)
        self.assertFalse(list(self.active.glob(".*.??????")))

    def test_corrupt_controller_backup_refuses_without_changes(self):
        (self.store / "legacy-controller").write_text("corrupt")
        self.assertNotEqual(self.run_watchdog("restore").returncode, 0)
        self.assertEqual(self.ctrl.read_text(), "candidate\n")
        self.assertEqual(self.hook.read_text(), "candidate\n")

    def test_corrupt_hook_backup_refuses_without_changes(self):
        (self.store / "legacy-ip-up-hook").write_text("corrupt")
        self.assertNotEqual(self.run_watchdog("restore").returncode, 0)
        self.assertEqual(self.ctrl.read_text(), "candidate\n")
        self.assertEqual(self.hook.read_text(), "candidate\n")

    def test_symlink_backup_refused(self):
        (self.store / "legacy-controller").unlink()
        (self.store / "legacy-controller").symlink_to(self.ctrl)
        self.assertNotEqual(self.run_watchdog("restore").returncode, 0)
        self.assertEqual(self.ctrl.read_text(), "candidate\n")

    def test_missing_backup_refused(self):
        (self.store / "legacy-ip-up-hook").unlink()
        self.assertNotEqual(self.run_watchdog("restore").returncode, 0)
        self.assertEqual(self.hook.read_text(), "candidate\n")

    def test_repeated_restore_idempotent(self):
        self.assertEqual(self.run_watchdog("restore").returncode, 0)
        self.assertEqual(self.run_watchdog("restore").returncode, 0)
        self.assertEqual(self.ctrl.read_bytes(), self.old_ctrl)

    def test_no_network_mutation_commands(self):
        script = SOURCE.read_text()
        for forbidden in ("tc qdisc add", "tc qdisc del", "tc filter del",
                          "ip link del", "ip link add", "systemctl restart",
                          "poff ", "pon "):
            self.assertNotIn(forbidden, script)

if __name__ == "__main__":
    unittest.main(verbosity=2)
