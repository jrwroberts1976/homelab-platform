"""Offline tests for OS and service identification."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
from scan_evidence import parse_host

IP = "192.168.2.20"

XML = f"""
<nmaprun>
  <host>
    <status state="up"/>
    <address addr="{IP}" addrtype="ipv4"/>
    <os><osmatch name="Linux 6.x" accuracy="92">
      <osclass osfamily="Linux" accuracy="92"/>
    </osmatch></os>
    <ports><port protocol="tcp" portid="22">
      <state state="open"/>
      <service name="ssh" product="OpenSSH" version="9.0"/>
    </port></ports>
  </host>
  <runstats><finished exit="success"/></runstats>
</nmaprun>
"""


class ScanEvidenceTests(unittest.TestCase):
    def test_linux_fingerprint(self):
        result = parse_host(XML, IP)
        self.assertEqual(result["os_matches"][0]["name"], "Linux 6.x")
        self.assertEqual(result["os_matches"][0]["accuracy"], "92")

    def test_open_port_and_service(self):
        port = parse_host(XML, IP)["ports"][0]
        self.assertEqual(port["port"], 22)
        self.assertEqual(port["service"]["product"], "OpenSSH")

    def test_windows_fingerprint(self):
        xml = XML.replace("Linux 6.x", "Windows 11").replace(
            'osfamily="Linux"', 'osfamily="Windows"'
        )
        self.assertEqual(
            parse_host(xml, IP)["os_matches"][0]["classes"][0]["os_family"],
            "Windows",
        )

    def test_unknown_os_not_guessed(self):
        xml = XML.replace(
            '<os><osmatch name="Linux 6.x" accuracy="92">\n'
            '      <osclass osfamily="Linux" accuracy="92"/>\n'
            '    </osmatch></os>', ""
        )
        self.assertEqual(parse_host(xml, IP)["os_matches"], [])

    def test_wrong_ip_rejected(self):
        with self.assertRaises(ValueError):
            parse_host(XML, "192.168.2.99")

    def test_incomplete_scan_rejected(self):
        with self.assertRaises(ValueError):
            parse_host(XML.replace('exit="success"', 'exit="error"'), IP)


if __name__ == "__main__":
    unittest.main()
