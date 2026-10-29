import importlib.util
import unittest
from pathlib import Path

SOURCE = (
    Path(__file__).resolve().parents[1]
    / "files/dhcp_forwarder.py"
)

spec = importlib.util.spec_from_file_location("dhcp_forwarder", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DHCPForwarderTests(unittest.TestCase):

    def setUp(self):
        self.entry = {
            "SYSLOG_IDENTIFIER": "dnsmasq-dhcp",
            "_SYSTEMD_UNIT": "dnsmasq.service",
            "SYSLOG_PID": "778",
            "MESSAGE": (
                "DHCPACK(eth0) 192.168.2.186 "
                "24:b2:b9:30:f8:55 James-LT"
            ),
        }

    def test_valid_dhcp_ack(self):
        result = module.format_event(self.entry)
        self.assertEqual(
            result,
            "dnsmasq-dhcp[778]: " + self.entry["MESSAGE"],
        )

    def test_reject_wrong_identifier(self):
        self.entry["SYSLOG_IDENTIFIER"] = "other"
        self.assertIsNone(module.format_event(self.entry))

    def test_reject_wrong_service(self):
        self.entry["_SYSTEMD_UNIT"] = "other.service"
        self.assertIsNone(module.format_event(self.entry))

    def test_reject_outside_subnet(self):
        self.entry["MESSAGE"] = (
            "DHCPACK(eth0) 10.0.0.10 "
            "24:b2:b9:30:f8:55"
        )
        self.assertIsNone(module.format_event(self.entry))

    def test_reject_wrong_interface(self):
        self.entry["MESSAGE"] = (
            "DHCPACK(eth1) 192.168.2.186 "
            "24:b2:b9:30:f8:55"
        )
        self.assertIsNone(module.format_event(self.entry))

    def test_reject_request(self):
        self.entry["MESSAGE"] = self.entry["MESSAGE"].replace(
            "DHCPACK", "DHCPREQUEST"
        )
        self.assertIsNone(module.format_event(self.entry))

    def test_reject_invalid_pid(self):
        self.entry["SYSLOG_PID"] = "invalid"
        self.assertIsNone(module.format_event(self.entry))

    def test_accept_missing_hostname(self):
        self.entry["MESSAGE"] = (
            "DHCPACK(eth0) 192.168.2.180 "
            "24:4b:fe:5e:cc:c8"
        )
        self.assertIsNotNone(module.format_event(self.entry))


if __name__ == "__main__":
    unittest.main()
