"""Offline integration tests for the complete profiling workflow."""
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
from profile_cycle import run_profile_once
from worker_lock import WorkerBusy, exclusive_worker_lock
from worker_state import load_state

MAC = "aa:bb:cc:dd:ee:02"
IP = "192.168.2.20"

XML = (
    '<nmaprun><host><status state="up"/>'
    f'<address addr="{IP}" addrtype="ipv4"/>'
    f'<address addr="{MAC}" addrtype="mac"/>'
    '<ports><port protocol="tcp" portid="22">'
    '<state state="open"/><service name="ssh"/>'
    '</port></ports></host>'
    '<runstats><finished exit="success"/></runstats></nmaprun>'
)


class ProfileCycleTests(unittest.TestCase):
    def test_successful_scan_holds_global_lock(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            collector = root / "devices.json"
            profiles = root / "profiles.json"
            lock = root / "worker.lock"

            collector.write_text(json.dumps({
                "schema_version": 1,
                "devices": {MAC: {
                    "status": "pending",
                    "last_ip": IP,
                    "last_inventory_seen": 995,
                    "discovered_at": 900,
                }},
            }))

            commands = []

            def fake_nmap(command, **kwargs):
                commands.append(command)

                if "-sS" in command or "-sU" in command:
                    with self.assertRaises(WorkerBusy):
                        with exclusive_worker_lock(lock):
                            pass

                xml = XML
                if "-sU" in command:
                    xml = xml.replace(
                        'protocol="tcp" portid="22"',
                        'protocol="udp" portid="53"',
                    )

                return SimpleNamespace(returncode=0, stdout=xml)

            result = run_profile_once(
                collector, profiles, lock, fake_nmap, now=1000
            )

            self.assertEqual(result["status"], "complete")
            record = load_state(profiles)["profiles"][MAC]
            self.assertEqual(record["status"], "complete")
            self.assertEqual(record["profile"]["tcp"]["ports"][0]["port"], 22)
            self.assertEqual(record["profile"]["udp"]["ports"][0]["port"], 53)
            self.assertEqual(sum("-sS" in c for c in commands), 1)
            self.assertEqual(sum("-sU" in c for c in commands), 1)
            self.assertEqual(sum("-sn" in c for c in commands), 3)

    def test_udp_timeout_preserves_tcp_profile(self):
        from subprocess import TimeoutExpired

        with TemporaryDirectory() as directory:
            root = Path(directory)
            collector = root / "devices.json"
            profiles = root / "profiles.json"
            lock = root / "worker.lock"

            collector.write_text(json.dumps({
                "schema_version": 1,
                "devices": {MAC: {
                    "status": "pending",
                    "last_ip": IP,
                    "last_inventory_seen": 995,
                    "discovered_at": 900,
                }},
            }))

            commands = []

            def fake_nmap(command, **kwargs):
                commands.append(command)
                if "-sU" in command:
                    raise TimeoutExpired(command, 650)
                return SimpleNamespace(returncode=0, stdout=XML)

            result = run_profile_once(
                collector, profiles, lock, fake_nmap, now=1000
            )

            record = load_state(profiles)["profiles"][MAC]
            self.assertEqual(result["status"], "partial")
            self.assertEqual(record["status"], "partial")
            self.assertEqual(
                record["profile"]["tcp"]["ports"][0]["port"], 22
            )
            self.assertIsNone(record["profile"]["udp"])
            self.assertIn("TimeoutExpired", record["last_error"])
            self.assertEqual(sum("-sS" in c for c in commands), 1)
            self.assertEqual(sum("-sU" in c for c in commands), 1)
            self.assertEqual(sum("-sn" in c for c in commands), 3)

    def test_ip_change_after_tcp_stops_udp(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            collector = root / "devices.json"
            profiles = root / "profiles.json"
            lock = root / "worker.lock"

            device = {
                "status": "pending",
                "last_ip": IP,
                "last_inventory_seen": 995,
                "discovered_at": 900,
            }

            def save_collector():
                collector.write_text(json.dumps({
                    "schema_version": 1,
                    "devices": {MAC: device},
                }))

            save_collector()
            commands = []

            def fake_nmap(command, **kwargs):
                commands.append(command)
                if "-sS" in command:
                    device["last_ip"] = "192.168.2.21"
                    save_collector()
                return SimpleNamespace(returncode=0, stdout=XML)

            result = run_profile_once(
                collector, profiles, lock, fake_nmap, now=1000
            )

            record = load_state(profiles)["profiles"][MAC]
            self.assertEqual(result["status"], "failed")
            self.assertEqual(record["status"], "failed")
            self.assertIn("Identity changed", record["last_error"])
            self.assertNotIn("profile", record)
            self.assertEqual(sum("-sS" in c for c in commands), 1)
            self.assertEqual(sum("-sU" in c for c in commands), 0)

    def test_ip_change_during_udp_rejects_profile(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            collector = root / "devices.json"
            profiles = root / "profiles.json"
            lock = root / "worker.lock"

            device = {
                "status": "pending",
                "last_ip": IP,
                "last_inventory_seen": 995,
                "discovered_at": 900,
            }

            def save_collector():
                collector.write_text(json.dumps({
                    "schema_version": 1,
                    "devices": {MAC: device},
                }))

            save_collector()
            commands = []

            def fake_nmap(command, **kwargs):
                commands.append(command)
                if "-sU" in command:
                    device["last_ip"] = "192.168.2.21"
                    save_collector()
                return SimpleNamespace(returncode=0, stdout=XML)

            result = run_profile_once(
                collector, profiles, lock, fake_nmap, now=1000
            )

            record = load_state(profiles)["profiles"][MAC]
            self.assertEqual(result["status"], "failed")
            self.assertEqual(record["status"], "failed")
            self.assertNotIn("profile", record)
            self.assertEqual(sum("-sS" in c for c in commands), 1)
            self.assertEqual(sum("-sU" in c for c in commands), 1)
            self.assertEqual(sum("-sn" in c for c in commands), 3)

    def test_mac_change_after_udp_rejects_profile(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            collector = root / "devices.json"
            profiles = root / "profiles.json"
            lock = root / "worker.lock"

            collector.write_text(json.dumps({
                "schema_version": 1,
                "devices": {MAC: {
                    "status": "pending",
                    "last_ip": IP,
                    "last_inventory_seen": 995,
                    "discovered_at": 900,
                }},
            }))

            commands = []
            arp_checks = 0

            def fake_nmap(command, **kwargs):
                nonlocal arp_checks
                commands.append(command)
                if "-sn" in command:
                    arp_checks += 1
                    if arp_checks == 3:
                        return SimpleNamespace(
                            returncode=0,
                            stdout=XML.replace(
                                MAC, "aa:bb:cc:dd:ee:ff"
                            ),
                        )
                return SimpleNamespace(returncode=0, stdout=XML)

            result = run_profile_once(
                collector, profiles, lock, fake_nmap, now=1000
            )

            record = load_state(profiles)["profiles"][MAC]
            self.assertEqual(result["status"], "failed")
            self.assertEqual(record["status"], "failed")
            self.assertNotIn("profile", record)
            self.assertEqual(arp_checks, 3)
            self.assertEqual(sum("-sS" in c for c in commands), 1)
            self.assertEqual(sum("-sU" in c for c in commands), 1)

    def test_tcp_timeout_records_failure_and_releases_lock(self):
        from subprocess import TimeoutExpired

        with TemporaryDirectory() as directory:
            root = Path(directory)
            collector = root / "devices.json"
            profiles = root / "profiles.json"
            lock = root / "worker.lock"

            collector.write_text(json.dumps({
                "schema_version": 1,
                "devices": {MAC: {
                    "status": "pending",
                    "last_ip": IP,
                    "last_inventory_seen": 995,
                    "discovered_at": 900,
                }},
            }))

            commands = []

            def fake_nmap(command, **kwargs):
                commands.append(command)
                if "-sS" in command:
                    raise TimeoutExpired(command, 1250)
                return SimpleNamespace(returncode=0, stdout=XML)

            result = run_profile_once(
                collector, profiles, lock, fake_nmap, now=1000
            )

            record = load_state(profiles)["profiles"][MAC]
            self.assertEqual(result["status"], "failed")
            self.assertEqual(record["status"], "failed")
            self.assertIn("TimeoutExpired", record["last_error"])
            self.assertNotIn("profile", record)
            self.assertEqual(sum("-sS" in c for c in commands), 1)
            self.assertEqual(sum("-sU" in c for c in commands), 0)

            with exclusive_worker_lock(lock):
                pass

    def test_stale_device_does_not_block_new_device(self):
        fresh_mac = "aa:bb:cc:dd:ee:03"
        fresh_ip = "192.168.2.21"

        with TemporaryDirectory() as directory:
            root = Path(directory)
            collector = root / "devices.json"
            profiles = root / "profiles.json"
            lock = root / "worker.lock"

            collector.write_text(json.dumps({
                "schema_version": 1,
                "devices": {
                    MAC: {
                        "status": "pending",
                        "last_ip": IP,
                        "last_inventory_seen": 100,
                        "discovered_at": 800,
                    },
                    fresh_mac: {
                        "status": "pending",
                        "last_ip": fresh_ip,
                        "last_inventory_seen": 995,
                        "discovered_at": 900,
                    },
                },
            }))

            fresh_xml = XML.replace(IP, fresh_ip).replace(
                MAC, fresh_mac
            )

            def fake_nmap(command, **kwargs):
                return SimpleNamespace(
                    returncode=0, stdout=fresh_xml
                )

            result = run_profile_once(
                collector, profiles, lock, fake_nmap, now=1000
            )

            self.assertIsNotNone(result)
            self.assertEqual(result["mac"], fresh_mac)
            self.assertEqual(result["status"], "complete")

    def test_stale_device_reenters_after_fresh_dhcp(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            collector = root / "devices.json"
            profiles = root / "profiles.json"
            lock = root / "worker.lock"

            device = {
                "status": "pending",
                "last_ip": IP,
                "last_inventory_seen": 100,
                "discovered_at": 90,
            }

            def save_collector():
                collector.write_text(json.dumps({
                    "schema_version": 1,
                    "devices": {MAC: device},
                }))

            calls = []

            def fake_nmap(command, **kwargs):
                calls.append(command)
                return SimpleNamespace(returncode=0, stdout=XML)

            save_collector()

            # A stale device must not trigger any scanning.
            self.assertIsNone(run_profile_once(
                collector, profiles, lock, fake_nmap, now=1000
            ))
            self.assertEqual(calls, [])

            # A fresh DHCP event makes the same MAC eligible again.
            device["last_inventory_seen"] = 995
            save_collector()

            result = run_profile_once(
                collector, profiles, lock, fake_nmap, now=1000
            )
            self.assertEqual(result["status"], "complete")
            self.assertEqual(result["mac"], MAC)
            self.assertEqual(
                load_state(profiles)["profiles"][MAC]["status"],
                "complete",
            )
