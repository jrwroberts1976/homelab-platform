import importlib.util
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

source = Path(__file__).resolve().parents[1] / "files/dhcp_forwarder.py"
spec = importlib.util.spec_from_file_location("forwarder_cleanup", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ProcessCleanupTests(unittest.TestCase):
    def test_child_terminated_when_forwarding_fails(self):
        process = MagicMock()
        process.poll.side_effect = [None, 0]
        process.stdout = MagicMock()
        process.stdout.__iter__.return_value = iter([])

        with (
            patch("subprocess.Popen", return_value=process),
            patch("socket.socket"),
            patch.object(
                module,
                "forward_entries",
                side_effect=RuntimeError("simulated failure"),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "simulated failure"):
                module.run("192.168.2.52", 5514)

        process.terminate.assert_called_once()
        process.wait.assert_called_once_with(timeout=5)
        process.stdout.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()


class ForcedKillTests(unittest.TestCase):
    def test_child_killed_after_termination_timeout(self):
        import subprocess

        process = MagicMock()
        process.poll.return_value = None
        process.stdout = MagicMock()
        process.stdout.__iter__.return_value = iter([])
        process.wait.side_effect = [
            subprocess.TimeoutExpired("journalctl", 5),
            0,
        ]

        with (
            patch("subprocess.Popen", return_value=process),
            patch("socket.socket"),
        ):
            with self.assertRaisesRegex(
                RuntimeError, "journalctl stream ended"
            ):
                module.run("192.168.2.52", 5514)

        process.terminate.assert_called_once()
        process.kill.assert_called_once()
        self.assertEqual(process.wait.call_count, 2)
        process.stdout.close.assert_called_once()
