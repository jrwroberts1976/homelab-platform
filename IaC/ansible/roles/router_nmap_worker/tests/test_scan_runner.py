"""Offline tests for TCP and UDP scan execution."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
from scan_runner import scan_tcp, scan_udp

IP = "192.168.2.20"
XML = (
    '<nmaprun><host><status state="up"/>'
    f'<address addr="{IP}" addrtype="ipv4"/>'
    '<ports><port protocol="tcp" portid="22">'
    '<state state="open"/>'
    '<service name="ssh" product="OpenSSH"/>'
    '</port></ports></host>'
    '<runstats><finished exit="success"/></runstats></nmaprun>'
)


class ScanRunnerTests(unittest.TestCase):
    def setUp(self):
        self.calls = []

    def fake_runner(self, command, **kwargs):
        self.calls.append((command, kwargs))
        return SimpleNamespace(returncode=0, stdout=XML)

    def test_tcp_command_and_evidence(self):
        result = scan_tcp(IP, self.fake_runner)
        command, options = self.calls[0]
        self.assertIn("-sS", command)
        self.assertIn("-O", command)
        self.assertIn("-p-", command)
        self.assertEqual(options["timeout"], 1250)
        self.assertEqual(result["ports"][0]["port"], 22)

    def test_udp_command_and_timeout(self):
        scan_udp(IP, self.fake_runner)
        command, options = self.calls[0]
        self.assertIn("-sU", command)
        self.assertIn("--send-eth", command)
        self.assertTrue(any(arg.startswith("53,67,68,") for arg in command))
        self.assertEqual(options["timeout"], 650)

    def test_external_target_rejected(self):
        with self.assertRaises(ValueError):
            scan_tcp("8.8.8.8", self.fake_runner)
        self.assertEqual(self.calls, [])

    def test_failed_nmap_rejected(self):
        def failed_runner(command, **kwargs):
            return SimpleNamespace(returncode=1, stdout=XML)

        with self.assertRaises(RuntimeError):
            scan_tcp(IP, failed_runner)
