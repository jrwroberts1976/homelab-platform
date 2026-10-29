import importlib.util
import json
import unittest
from pathlib import Path

source = (
    Path(__file__).resolve().parents[1]
    / "files/dhcp_forwarder.py"
)
spec = importlib.util.spec_from_file_location("forwarder_transport", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TransportTests(unittest.TestCase):

    def test_only_valid_dhcp_ack_is_forwarded(self):
        valid = {
            "SYSLOG_IDENTIFIER": "dnsmasq-dhcp",
            "_SYSTEMD_UNIT": "dnsmasq.service",
            "SYSLOG_PID": "778",
            "MESSAGE": (
                "DHCPACK(eth0) 192.168.2.186 "
                "24:b2:b9:30:f8:55 James-LT"
            ),
        }

        invalid = {**valid, "MESSAGE": "DHCPREQUEST(eth0)"}
        packets = []

        count = module.forward_entries(
            [
                json.dumps(valid),
                json.dumps(invalid),
                "invalid json",
            ],
            packets.append,
        )

        self.assertEqual(count, 1)
        self.assertEqual(len(packets), 1)
        self.assertIn(b"DHCPACK(eth0)", packets[0])


if __name__ == "__main__":
    unittest.main()
