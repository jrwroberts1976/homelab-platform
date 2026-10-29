import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

source = (
    Path(__file__).resolve().parents[1]
    / "files/dhcp_forwarder.py"
)
spec = importlib.util.spec_from_file_location("dhcp_forwarder_packet", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SyslogPacketTests(unittest.TestCase):

    def test_valid_packet(self):
        entry = {
            "SYSLOG_IDENTIFIER": "dnsmasq-dhcp",
            "_SYSTEMD_UNIT": "dnsmasq.service",
            "SYSLOG_PID": "778",
            "MESSAGE": (
                "DHCPACK(eth0) 192.168.2.186 "
                "24:b2:b9:30:f8:55 James-LT"
            ),
        }

        packet = module.format_syslog_packet(entry)
        self.assertIsInstance(packet, bytes)
        self.assertTrue(packet.startswith(b"<134>"))
        self.assertIn(b"router-01 dnsmasq-dhcp[778]: DHCPACK", packet)

    def test_reject_other_service(self):
        entry = {
            "SYSLOG_IDENTIFIER": "other",
            "_SYSTEMD_UNIT": "other.service",
            "MESSAGE": "unrelated",
        }
        self.assertIsNone(module.format_syslog_packet(entry))
