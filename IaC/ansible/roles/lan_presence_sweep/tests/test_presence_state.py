import sys
import unittest
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "files")
)
from presence_state import empty_state, merge_sweep

MAC = "b8:27:eb:e8:36:cd"
OTHER = "00:1c:2b:5a:6d:fd"


class PresenceTests(unittest.TestCase):
    def setUp(self):
        self.first = merge_sweep(
            empty_state(), {MAC: "192.168.2.48"}, 1000
        )

    def test_first_discovery(self):
        device = self.first["devices"][MAC]
        self.assertTrue(device["observed"])
        self.assertEqual(device["last_seen"], 1000)

    def test_missing_device_preserves_last_seen(self):
        result = merge_sweep(
            self.first, {OTHER: "192.168.2.7"}, 1600
        )
        device = result["devices"][MAC]
        self.assertFalse(device["observed"])
        self.assertEqual(device["last_seen"], 1000)

    def test_returning_device_updates_address(self):
        result = merge_sweep(
            self.first, {MAC: "192.168.2.49"}, 1600
        )
        device = result["devices"][MAC]
        self.assertEqual(device["first_seen"], 1000)
        self.assertEqual(device["last_seen"], 1600)
        self.assertEqual(device["last_ip"], "192.168.2.49")

    def test_failed_sweep_preserves_state(self):
        with self.assertRaises(ValueError):
            merge_sweep(self.first, {}, 1600)
        self.assertTrue(self.first["devices"][MAC]["observed"])


    def test_duplicate_ip_is_rejected(self):
        with self.assertRaises(ValueError):
            merge_sweep(
                self.first,
                {MAC: "192.168.2.48", OTHER: "192.168.2.48"},
                1600,
            )

    def test_old_sweep_is_rejected(self):
        with self.assertRaises(ValueError):
            merge_sweep(
                self.first, {MAC: "192.168.2.48"}, 900
            )

    def test_invalid_mac_is_rejected(self):
        with self.assertRaises(ValueError):
            merge_sweep(
                self.first, {"invalid": "192.168.2.48"}, 1600
            )


if __name__ == "__main__":
    unittest.main()
