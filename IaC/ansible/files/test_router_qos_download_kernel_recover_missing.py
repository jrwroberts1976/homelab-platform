#!/usr/bin/env python3
"""Offline guard tests for create-only kernel recovery. Never contact router."""
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).with_name("router-qos-download-kernel-recover-missing.sh")

class KernelRecoveryActorTests(unittest.TestCase):
    def test_shell_syntax(self):
        p = subprocess.run(["bash", "-n", str(SOURCE)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_commands_are_create_only(self):
        source = SOURCE.read_text()
        for forbidden in ("ip link del", "tc qdisc del", "tc filter del",
                          "tc qdisc replace", "tc filter replace",
                          "systemctl restart", "pppoe-stop", "ip route"):
            self.assertNotIn(forbidden, source)

    def test_invalid_mode_fails_before_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            script = SOURCE.read_text().replace(
                '[[ ${EUID} -eq 0 && "$(hostname -s)" == raspberrypi ]] || exit 2',
                'true'
            )
            p = Path(directory) / "actor.sh"
            p.write_text(script)
            result = subprocess.run(["bash", str(p), "status"],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("REFUSE: command", result.stderr)

    def test_absent_approval_fails_before_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            script = SOURCE.read_text().replace(
                '[[ ${EUID} -eq 0 && "$(hostname -s)" == raspberrypi ]] || exit 2',
                'true'
            ).replace(
                'APPROVAL=/run/router-qos-download-kernel-recovery.approved',
                f'APPROVAL={directory}/not-approved'
            )
            p = Path(directory) / "actor.sh"
            p.write_text(script)
            result = subprocess.run(["bash", str(p), "restore-missing"],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("approval absent", result.stderr)

if __name__ == "__main__":
    unittest.main(verbosity=2)
