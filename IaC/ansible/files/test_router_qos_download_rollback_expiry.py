#!/usr/bin/env python3
"""Offline expiry-gate tests. No router, systemd, network, or live files."""
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).with_name("router-qos-download-rollback-expiry.sh")

class ExpiryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.marker = root / "pending"
        self.calls = root / "calls"
        restore = root / "restore.sh"
        restore.write_text("#!/bin/sh\nprintf '%s\\n' \"$1\" >> " + str(self.calls) + "\n")
        restore.chmod(0o700)
        source = SOURCE.read_text()
        replacements = {
            '[[ $EUID -eq 0 && "$(hostname -s)" == raspberrypi ]] || exit 2': 'true',
            'MARKER=/run/router-qos-download-cutover.pending': f'MARKER={self.marker}',
            'RESTORE=/usr/local/libexec/router-qos-download-cutover/rollback-watchdog.sh': f'RESTORE={restore}',
        }
        for old, new in replacements.items():
            self.assertIn(old, source)
            source = source.replace(old, new)
        self.script = root / "expiry.sh"
        self.script.write_text(source)

    def run_expiry(self):
        return subprocess.run(["bash", str(self.script)], capture_output=True,
                              text=True, timeout=5)

    def test_missing_marker_noop(self):
        self.assertEqual(self.run_expiry().returncode, 0)
        self.assertFalse(self.calls.exists())

    def test_armed_marker_calls_restore_once(self):
        self.marker.write_text("pending")
        result = self.run_expiry()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls.read_text(), "restore\n")

    def test_cancelled_marker_noop(self):
        self.marker.write_text("pending")
        self.marker.unlink()
        self.assertEqual(self.run_expiry().returncode, 0)
        self.assertFalse(self.calls.exists())

    def test_symlink_marker_refused(self):
        target = self.marker.parent / "target"
        target.write_text("pending")
        self.marker.symlink_to(target)
        self.assertNotEqual(self.run_expiry().returncode, 0)
        self.assertFalse(self.calls.exists())

    def test_directory_marker_refused(self):
        self.marker.mkdir()
        self.assertNotEqual(self.run_expiry().returncode, 0)
        self.assertFalse(self.calls.exists())

    def test_timer_has_no_boot_catchup_and_requires_activation(self):
        timer = SOURCE.with_name("router-qos-download-rollback-expiry.timer").read_text()
        self.assertIn("OnActiveSec=10min", timer)
        self.assertIn("Persistent=false", timer)
        self.assertNotIn("OnBootSec=", timer)
        service = SOURCE.with_name("router-qos-download-rollback-expiry.service").read_text()
        self.assertIn("ConditionPathExists=/run/router-qos-download-cutover.pending", service)

if __name__ == "__main__":
    unittest.main(verbosity=2)
