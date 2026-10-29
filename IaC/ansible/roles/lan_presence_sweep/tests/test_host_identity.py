import sys
import unittest
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "files")
)
from host_identity import verified_hostnames, attach_verified_hostnames
from presence_state import empty_state, merge_sweep

MAC = "b8:27:eb:e8:36:cd"
IP = "192.168.2.48"


def host(name="admin-01", ip=IP, mac=MAC):
    return {"metric": {
        "target_name": name,
        "instance": ip + ":9100",
        "address": mac,
    }}


class HostIdentityTests(unittest.TestCase):
    def test_verified_host(self):
        self.assertEqual(
            verified_hostnames({MAC: IP}, [host()]),
            {MAC: "admin-01"},
        )

    def test_stale_ip_rejected(self):
        self.assertEqual(
            verified_hostnames({MAC: "192.168.2.49"}, [host()]),
            {},
        )

    def test_incorrect_mac_rejected(self):
        self.assertEqual(
            verified_hostnames(
                {MAC: IP},
                [host(mac="00:11:22:33:44:55")],
            ),
            {},
        )

    def test_conflicting_hostnames_rejected(self):
        self.assertEqual(
            verified_hostnames(
                {MAC: IP},
                [host("admin-01"), host("different-host")],
            ),
            {},
        )


    def test_hostname_survives_missing_sweep(self):
        first = merge_sweep(empty_state(), {MAC: IP}, 1000)
        named = attach_verified_hostnames(
            first, {MAC: "admin-01"}, 1000
        )
        missing = merge_sweep(
            named,
            {"00:1c:2b:5a:6d:fd": "192.168.2.7"},
            1600,
        )
        record = missing["devices"][MAC]
        self.assertFalse(record["observed"])
        self.assertEqual(record["target_name"], "admin-01")
        self.assertEqual(record["last_seen"], 1000)

    def test_unobserved_mac_cannot_gain_hostname(self):
        state = merge_sweep(empty_state(), {MAC: IP}, 1000)
        result = attach_verified_hostnames(
            state, {"00:11:22:33:44:55": "other-host"}, 1000
        )
        self.assertNotIn(
            "target_name", result["devices"][MAC]
        )

    def test_invalid_hostname_is_rejected(self):
        state = merge_sweep(empty_state(), {MAC: IP}, 1000)
        with self.assertRaises(ValueError):
            attach_verified_hostnames(state, {MAC: ""}, 1000)


if __name__ == "__main__":
    unittest.main()
