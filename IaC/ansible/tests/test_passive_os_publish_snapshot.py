#!/usr/bin/env python3
"""Focused KISS tests for the passive OS read-only snapshot publisher."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from passive_os_publish_snapshot import publish


class SnapshotPublishTests(unittest.TestCase):
    def test_unprivileged_caller_refused_before_any_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("passive_os_publish_snapshot.os.geteuid", return_value=1000):
                with self.assertRaisesRegex(PermissionError, "Root required"):
                    publish(directory=Path(tmp) / "not-created")
            self.assertFalse((Path(tmp) / "not-created").exists())

    def test_outbound_directory_symlink_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "real").mkdir()
            (root / "outbound").symlink_to(root / "real", target_is_directory=True)
            with patch("passive_os_publish_snapshot.os.geteuid", return_value=0):
                with patch("passive_os_publish_snapshot.pwd.getpwnam"):
                    with self.assertRaisesRegex(ValueError, "Symlinked outbound"):
                        publish(directory=root / "outbound")

    def test_missing_identity_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "outbound"
            with patch("passive_os_publish_snapshot.os.geteuid", return_value=0):
                with patch("passive_os_publish_snapshot.pwd.getpwnam",
                           side_effect=KeyError("missing")):
                    with self.assertRaises(KeyError):
                        publish(directory=output)
            self.assertFalse(output.exists())

    def test_source_not_acknowledged(self):
        source = (Path(__file__).resolve().parents[1] / "scripts" /
                  "passive_os_publish_snapshot.py").read_text()
        self.assertIn('export_batch(pending, "get-batch")', source)
        self.assertNotIn("ack(spool", source)
        self.assertNotIn("checkpoint_path", source)
        self.assertNotIn("eve.json", source)
        self.assertNotIn("subprocess", source)


if __name__ == "__main__":
    unittest.main()
