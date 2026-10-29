import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
from sweep_runner import run_discovery

LOCAL_MAC = "bc:24:11:0b:16:a2"
ROUTER_MAC = "24:4b:fe:5e:cc:c8"


def scan_xml(mac=ROUTER_MAC):
    return (
        '<nmaprun><host><status state="up"/>'
        '<address addr="192.168.2.1" addrtype="ipv4"/>'
        f'<address addr="{mac}" addrtype="mac"/>'
        '</host><runstats><finished exit="success"/>'
        '<hosts up="1" down="255" total="256"/>'
        '</runstats></nmaprun>'
    )


class SweepRunnerTests(unittest.TestCase):
    def test_discovers_router_and_local_host(self):
        with (
            patch("sweep_runner.subprocess.check_output",
                  return_value="2: eth0 inet 192.168.2.52/24"),
            patch("sweep_runner.subprocess.run",
                  return_value=SimpleNamespace(
                      stdout=scan_xml()
                  )) as nmap,
            patch("sweep_runner.Path.read_text",
                  return_value=LOCAL_MAC + "\n"),
        ):
            result = run_discovery()

        self.assertEqual(result[ROUTER_MAC], "192.168.2.1")
        self.assertEqual(result[LOCAL_MAC], "192.168.2.52")
        self.assertIn("192.168.2.0/24", nmap.call_args.args[0])

    def test_oversized_subnet_is_rejected(self):
        with (
            patch("sweep_runner.subprocess.check_output",
                  return_value="2: eth0 inet 192.168.2.52/16"),
            patch("sweep_runner.subprocess.run") as nmap,
        ):
            with self.assertRaises(ValueError):
                run_discovery()
            nmap.assert_not_called()

    def test_conflicting_local_mac_is_rejected(self):
        with (
            patch("sweep_runner.subprocess.check_output",
                  return_value="2: eth0 inet 192.168.2.52/24"),
            patch("sweep_runner.subprocess.run",
                  return_value=SimpleNamespace(
                      stdout=scan_xml(LOCAL_MAC)
                  )),
            patch("sweep_runner.Path.read_text",
                  return_value=LOCAL_MAC + "\n"),
        ):
            with self.assertRaises(ValueError):
                run_discovery()


if __name__ == "__main__":
    unittest.main()
