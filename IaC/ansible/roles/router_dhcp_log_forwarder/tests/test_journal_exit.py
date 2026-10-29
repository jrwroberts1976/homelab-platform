import importlib.util
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

source = Path(__file__).resolve().parents[1] / "files/dhcp_forwarder.py"
spec = importlib.util.spec_from_file_location("forwarder_exit", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class JournalExitTests(unittest.TestCase):
    def test_unexpected_clean_exit_is_failure(self):
        process = MagicMock()
        process.__enter__.return_value = process
        process.stdout = iter([])
        process.poll.return_value = 0

        with (
            patch("subprocess.Popen", return_value=process),
            patch("socket.socket") as socket_mock,
        ):
            socket_mock.return_value.__enter__.return_value = MagicMock()

            with self.assertRaisesRegex(
                RuntimeError, "journalctl stream ended"
            ):
                module.run("192.168.2.52", 5514)
