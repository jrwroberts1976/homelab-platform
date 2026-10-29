"""Offline tests for the live-scanning approval gate."""
import io
import json
import stat
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
import worker_main


class FakeConfig:
    def __init__(self, data):
        self.data = data
        self.mode = 0o600

    def lstat(self):
        return SimpleNamespace(
            st_mode=stat.S_IFREG | self.mode,
            st_uid=0,
        )

    def read_text(self):
        return json.dumps(self.data)


class WorkerMainTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "allow_live_scans": False,
            "expected_hostname": "monitor-01",
            "network": "192.168.2.0/24",
            "interface": "eth0",
            "collector_state": "/var/lib/collector/devices.json",
            "profile_state": "/var/lib/worker/profiles.json",
            "lock_path": "/var/lib/worker/worker.lock",
            "cooldown_seconds": 86400,
            "mail_host": "mail-relay-01",
            "mail_port": 25,
            "mail_from": "device-alert@jameshouse",
            "mail_to": "jrwroberts1976@gmail.com",
        }
        self.file = FakeConfig(self.config)
        self.enterContext(patch.object(worker_main, "CONFIG", self.file))
        self.enterContext(
            patch.object(worker_main.os, "geteuid", return_value=0)
        )
        self.enterContext(
            patch.object(
                worker_main.socket, "gethostname",
                return_value="monitor-01"
            )
        )
        self.scan = self.enterContext(
            patch.object(worker_main, "run_profile_once", return_value=None)
        )

    def test_disabled_approval_refuses_scan(self):
        with self.assertRaises(SystemExit):
            worker_main.main()
        self.scan.assert_not_called()

    def test_missing_approval_refuses_scan(self):
        del self.config["allow_live_scans"]
        with self.assertRaises(SystemExit):
            worker_main.main()
        self.scan.assert_not_called()

    def test_insecure_permissions_refuse_scan(self):
        self.config["allow_live_scans"] = True
        self.file.mode = 0o644
        with self.assertRaises(SystemExit):
            worker_main.main()
        self.scan.assert_not_called()

    def test_approved_configuration_uses_mock(self):
        self.config["allow_live_scans"] = True
        with patch.object(
            worker_main, "deliver_next_notification",
            return_value=None
        ) as delivery:
            with redirect_stdout(io.StringIO()):
                worker_main.main()
            delivery.assert_called_once()
        self.scan.assert_called_once()

    def test_non_root_execution_refused(self):
        self.config["allow_live_scans"] = True

        with patch.object(worker_main.os, "geteuid", return_value=1000):
            with self.assertRaises(SystemExit) as error:
                worker_main.main()

        self.assertIn("root privileges", str(error.exception))
        self.scan.assert_not_called()

    def test_wrong_hostname_refused(self):
        self.config["allow_live_scans"] = True

        with patch.object(
            worker_main.socket, "gethostname",
            return_value="admin-01"
        ):
            with self.assertRaises(SystemExit) as error:
                worker_main.main()

        self.assertIn("incorrect deployment host", str(error.exception))
        self.scan.assert_not_called()

    def test_configured_email_settings_are_used(self):
        self.config["allow_live_scans"] = True
        self.config["mail_host"] = "test-relay.internal"
        self.config["mail_port"] = 2525
        self.config["mail_from"] = "test-alert@jameshouse"
        self.config["mail_to"] = "jrwroberts1976@gmail.com"

        with patch.object(
            worker_main, "deliver_next_notification",
            return_value=None
        ) as delivery:
            with redirect_stdout(io.StringIO()):
                worker_main.main()

        delivery.assert_called_once_with(
            self.config["collector_state"],
            self.config["profile_state"],
            self.config["lock_path"],
            sender="test-alert@jameshouse",
            recipient="jrwroberts1976@gmail.com",
            host="test-relay.internal",
            port=2525,
        )
