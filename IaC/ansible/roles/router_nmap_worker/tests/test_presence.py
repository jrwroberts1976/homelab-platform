"""Offline tests for MAC/IP identity verification."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
from presence import verify_mac_ip

IP = "192.168.2.224"
MAC = "92:ff:53:0a:16:e9"


def result(mac=MAC, status="up", exit_status="success"):
    address = f'<address addr="{mac}" addrtype="mac"/>' if mac else ""
    host = (
        f'<host><status state="{status}"/>'
        f'<address addr="{IP}" addrtype="ipv4"/>'
        f'{address}</host>'
    )
    return (
        f'<nmaprun>{host}<runstats>'
        f'<finished exit="{exit_status}"/>'
        f'</runstats></nmaprun>'
    )


class PresenceTests(unittest.TestCase):
    def test_matching_identity(self):
        self.assertTrue(verify_mac_ip(result(), IP, MAC))

    def test_wrong_mac(self):
        self.assertFalse(verify_mac_ip(
            result(mac="aa:bb:cc:dd:ee:ff"), IP, MAC
        ))

    def test_missing_mac(self):
        self.assertFalse(verify_mac_ip(result(mac=""), IP, MAC))

    def test_offline_device(self):
        self.assertFalse(verify_mac_ip(
            result(status="down"), IP, MAC
        ))

    def test_failed_discovery(self):
        self.assertFalse(verify_mac_ip(
            result(exit_status="error"), IP, MAC
        ))

    def test_malformed_xml(self):
        self.assertFalse(verify_mac_ip("<invalid", IP, MAC))

    def test_duplicate_hosts(self):
        xml = result().replace("</host>", "</host>" * 1)
        host = xml.split("<host>")[1].split("</host>")[0]
        xml = xml.replace("</host>", "</host><host>" + host + "</host>", 1)
        self.assertFalse(verify_mac_ip(xml, IP, MAC))


if __name__ == "__main__":
    unittest.main()


class ProbeTests(unittest.TestCase):
    def test_matching_mac(self):
        from presence import probe_mac_ip
        from types import SimpleNamespace

        calls = []
        def fake_nmap(args, **kwargs):
            calls.append(args)
            return SimpleNamespace(returncode=0, stdout=result())

        self.assertTrue(probe_mac_ip(IP, MAC, fake_nmap))
        self.assertEqual(calls[0][-1], IP)
        self.assertIn("-PR", calls[0])

    def test_mismatched_mac(self):
        from presence import probe_mac_ip
        from types import SimpleNamespace

        fake = lambda *a, **k: SimpleNamespace(
            returncode=0, stdout=result(mac="aa:bb:cc:dd:ee:ff")
        )
        self.assertFalse(probe_mac_ip(IP, MAC, fake))

    def test_outside_lan_rejected(self):
        from presence import probe_mac_ip

        def must_not_run(*args, **kwargs):
            raise AssertionError("Nmap must not execute")

        with self.assertRaises(ValueError):
            probe_mac_ip("10.0.0.20", MAC, must_not_run)

    def test_invalid_interface_rejected(self):
        from presence import probe_mac_ip

        with self.assertRaises(ValueError):
            probe_mac_ip(IP, MAC, lambda *a, **k: None,
                         interface="eth0;invalid")
