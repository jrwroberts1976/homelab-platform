import sys
import unittest
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "files")
)
from sweep_parser import parse_sweep


def host(ip, mac=None, state="up"):
    address = (
        f'<address addr="{mac}" addrtype="mac"/>'
        if mac else ""
    )
    return (
        f'<host><status state="{state}"/>'
        f'<address addr="{ip}" addrtype="ipv4"/>'
        f'{address}</host>'
    )


class SweepParserTests(unittest.TestCase):
    def test_discovers_active_mac_addresses(self):
        xml = "<nmaprun>" + (
            host("192.168.2.48", "B8:27:EB:E8:36:CD")
            + host("192.168.2.49", state="down")
            + host("192.168.2.52")
        ) + "</nmaprun>"
        self.assertEqual(
            parse_sweep(xml),
            {"b8:27:eb:e8:36:cd": "192.168.2.48"},
        )

    def test_empty_discovery_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_sweep("<nmaprun></nmaprun>")

    def test_conflicting_mac_is_rejected(self):
        xml = "<nmaprun>" + (
            host("192.168.2.48", "B8:27:EB:E8:36:CD")
            + host("192.168.2.49", "B8:27:EB:E8:36:CD")
        ) + "</nmaprun>"
        with self.assertRaises(ValueError):
            parse_sweep(xml)


if __name__ == "__main__":
    unittest.main()
