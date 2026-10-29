import sys
import unittest
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "files")
)
from sweep_guard import validated_observations, check_population_drop

MAC = "b8:27:eb:e8:36:cd"


def result(exit_status="success", total=256, up=2):
    return (
        '<nmaprun>'
        '<host><status state="up"/>'
        '<address addr="192.168.2.48" addrtype="ipv4"/>'
        f'<address addr="{MAC}" addrtype="mac"/></host>'
        '<runstats>'
        f'<finished exit="{exit_status}"/>'
        f'<hosts up="{up}" down="254" total="{total}"/>'
        '</runstats></nmaprun>'
    )


class SweepGuardTests(unittest.TestCase):
    def test_completed_sweep(self):
        self.assertEqual(
            validated_observations(result(), 256),
            {MAC: "192.168.2.48"},
        )

    def test_interrupted_sweep(self):
        with self.assertRaises(ValueError):
            validated_observations(result(exit_status="error"), 256)

    def test_incomplete_sweep(self):
        with self.assertRaises(ValueError):
            validated_observations(result(total=128), 256)

    def test_inconsistent_host_count(self):
        with self.assertRaises(ValueError):
            validated_observations(result(up=0), 256)


    def test_large_population_drop_is_rejected(self):
        macs = [f"00:11:22:33:44:{i:02x}" for i in range(10)]
        previous = {
            "devices": {
                mac: {"observed": True} for mac in macs
            }
        }
        with self.assertRaises(ValueError):
            check_population_drop(
                previous, {mac: "192.168.2.1" for mac in macs[:3]}
            )

    def test_normal_population_drop_is_allowed(self):
        macs = [f"00:11:22:33:44:{i:02x}" for i in range(10)]
        previous = {
            "devices": {
                mac: {"observed": True} for mac in macs
            }
        }
        check_population_drop(
            previous, {mac: "192.168.2.1" for mac in macs[:4]}
        )

    def test_small_inventory_is_not_blocked(self):
        previous = {
            "devices": {
                "00:11:22:33:44:01": {"observed": True}
            }
        }
        check_population_drop(
            previous, {"00:11:22:33:44:02": "192.168.2.2"}
        )


if __name__ == "__main__":
    unittest.main()
