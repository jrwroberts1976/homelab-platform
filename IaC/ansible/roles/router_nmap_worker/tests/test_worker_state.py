"""Offline tests for persistent Nmap worker state."""
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
from worker_state import load_state, save_state


class WorkerStateTests(unittest.TestCase):
    def test_persistence_and_restart(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "worker.json"
            state = {"schema_version": 1, "profiles": {
                "aa:bb:cc:dd:ee:ff": {"status": "pending"}
            }}
            save_state(path, state)
            self.assertEqual(load_state(path), state)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_missing_state(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "missing.json"
            self.assertEqual(load_state(path)["profiles"], {})

    def test_corrupt_state_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "worker.json"
            path.write_text("{invalid")
            with self.assertRaises(ValueError):
                load_state(path)


class ReservationTests(unittest.TestCase):
    def test_reservation_survives_restart(self):
        from worker_state import reserve_scan
        with TemporaryDirectory() as directory:
            path = Path(directory) / "worker.json"
            mac, ip = "aa:bb:cc:dd:ee:02", "192.168.2.20"

            self.assertTrue(reserve_scan(path, mac, ip, 1000))
            record = load_state(path)["profiles"][mac]
            self.assertEqual(record["status"], "reserved")
            self.assertEqual(record["attempt_count"], 1)

            self.assertFalse(reserve_scan(path, mac, ip, 1001))
            self.assertEqual(
                load_state(path)["profiles"][mac]["attempt_count"], 1
            )

    def test_retry_after_cooldown(self):
        from worker_state import reserve_scan
        with TemporaryDirectory() as directory:
            path = Path(directory) / "worker.json"
            mac, ip = "aa:bb:cc:dd:ee:02", "192.168.2.20"

            self.assertTrue(reserve_scan(path, mac, ip, 1000))
            self.assertTrue(reserve_scan(path, mac, ip, 87400))
            self.assertEqual(
                load_state(path)["profiles"][mac]["attempt_count"], 2
            )

    def test_completed_device_not_reserved_again(self):
        from worker_state import reserve_scan
        with TemporaryDirectory() as directory:
            path = Path(directory) / "worker.json"
            save_state(path, {"schema_version": 1, "profiles": {
                "aa:bb:cc:dd:ee:02": {"status": "complete"}
            }})
            self.assertFalse(reserve_scan(
                path, "aa:bb:cc:dd:ee:02", "192.168.2.20", 100000
            ))


class ScanFailureTests(unittest.TestCase):
    def test_failure_preserves_history_and_cooldown(self):
        from worker_state import reserve_scan, mark_scan_failed
        with TemporaryDirectory() as directory:
            path = Path(directory) / "worker.json"
            mac, ip = "aa:bb:cc:dd:ee:02", "192.168.2.20"

            self.assertTrue(reserve_scan(path, mac, ip, 1000))
            mark_scan_failed(path, mac, ip, "Nmap timed out")

            record = load_state(path)["profiles"][mac]
            self.assertEqual(record["status"], "failed")
            self.assertEqual(record["last_error"], "Nmap timed out")
            self.assertEqual(record["attempt_count"], 1)
            self.assertEqual(record["last_attempt"], 1000)
            self.assertFalse(reserve_scan(path, mac, ip, 1001))
            self.assertTrue(reserve_scan(path, mac, ip, 87400))

    def test_failure_requires_matching_reservation(self):
        from worker_state import reserve_scan, mark_scan_failed
        with TemporaryDirectory() as directory:
            path = Path(directory) / "worker.json"
            mac = "aa:bb:cc:dd:ee:02"
            reserve_scan(path, mac, "192.168.2.20", 1000)

            with self.assertRaises(ValueError):
                mark_scan_failed(
                    path, mac, "192.168.2.21", "Wrong target"
                )
            self.assertEqual(
                load_state(path)["profiles"][mac]["status"],
                "reserved",
            )


class ScanCompletionTests(unittest.TestCase):
    def setUp(self):
        import json
        from worker_state import reserve_scan

        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.state = root / "worker.json"
        self.collector = root / "devices.json"
        self.mac = "aa:bb:cc:dd:ee:02"
        self.ip = "192.168.2.20"
        self.device = {
            "status": "pending",
            "last_ip": self.ip,
            "last_inventory_seen": 995,
        }
        self.collector.write_text(json.dumps({
            "schema_version": 1,
            "devices": {self.mac: self.device},
        }))
        self.assertTrue(reserve_scan(
            self.state, self.mac, self.ip, 1000
        ))
        self.tcp = {"os_matches": [{"name": "Linux"}], "ports": []}
        self.udp = {"os_matches": [], "ports": []}

        from types import SimpleNamespace
        xml = (
            '<nmaprun><host><status state="up"/>'
            f'<address addr="{self.ip}" addrtype="ipv4"/>'
            f'<address addr="{self.mac}" addrtype="mac"/>'
            '</host><runstats><finished exit="success"/>'
            '</runstats></nmaprun>'
        )
        self.fake_nmap = lambda *a, **k: SimpleNamespace(
            returncode=0, stdout=xml
        )

    def test_successful_completion(self):
        from worker_state import mark_scan_complete
        mark_scan_complete(
            self.state, self.collector, self.mac, self.ip,
            self.tcp, self.udp, 1000, self.fake_nmap
        )
        record = load_state(self.state)["profiles"][self.mac]
        self.assertEqual(record["status"], "complete")
        self.assertEqual(record["profiled_ip"], self.ip)
        self.assertEqual(record["profile"]["tcp"], self.tcp)

    def test_ip_change_rejects_results(self):
        import json
        from worker_state import mark_scan_complete
        self.device["last_ip"] = "192.168.2.21"
        self.collector.write_text(json.dumps({
            "schema_version": 1,
            "devices": {self.mac: self.device},
        }))
        with self.assertRaises(RuntimeError):
            mark_scan_complete(
                self.state, self.collector, self.mac, self.ip,
                self.tcp, self.udp, 1000, self.fake_nmap
            )
        self.assertEqual(
            load_state(self.state)["profiles"][self.mac]["status"],
            "reserved",
        )

    def test_wrong_mac_blocks_completion(self):
        from types import SimpleNamespace
        from worker_state import mark_scan_complete

        wrong_xml = self.fake_nmap().stdout.replace(
            self.mac, "aa:bb:cc:dd:ee:ff"
        )
        fake_wrong_mac = lambda *a, **k: SimpleNamespace(
            returncode=0, stdout=wrong_xml
        )

        with self.assertRaises(RuntimeError):
            mark_scan_complete(
                self.state, self.collector, self.mac, self.ip,
                self.tcp, self.udp, 1000, fake_wrong_mac
            )

        record = load_state(self.state)["profiles"][self.mac]
        self.assertEqual(record["status"], "reserved")
        self.assertEqual(record["attempt_count"], 1)
        self.assertNotIn("profile", record)

    def test_partial_preserves_tcp_evidence(self):
        from worker_state import mark_scan_partial

        mark_scan_partial(
            self.state, self.collector, self.mac, self.ip,
            self.tcp, 1000, self.fake_nmap, "UDP timed out"
        )
        record = load_state(self.state)["profiles"][self.mac]

        self.assertEqual(record["status"], "partial")
        self.assertEqual(record["profile"]["tcp"], self.tcp)
        self.assertIsNone(record["profile"]["udp"])
        self.assertEqual(record["last_error"], "UDP timed out")
        self.assertEqual(record["attempt_count"], 1)

    def test_partial_rejects_wrong_mac(self):
        from types import SimpleNamespace
        from worker_state import mark_scan_partial

        xml = self.fake_nmap().stdout.replace(
            self.mac, "aa:bb:cc:dd:ee:ff"
        )
        runner = lambda *a, **k: SimpleNamespace(
            returncode=0, stdout=xml
        )
        with self.assertRaises(RuntimeError):
            mark_scan_partial(
                self.state, self.collector, self.mac, self.ip,
                self.tcp, 1000, runner, "UDP timed out"
            )
        record = load_state(self.state)["profiles"][self.mac]
        self.assertEqual(record["status"], "reserved")
        self.assertNotIn("profile", record)

    def test_partial_rejects_changed_ip(self):
        import json
        from worker_state import mark_scan_partial

        self.device["last_ip"] = "192.168.2.21"
        self.collector.write_text(json.dumps({
            "schema_version": 1,
            "devices": {self.mac: self.device},
        }))
        with self.assertRaises(RuntimeError):
            mark_scan_partial(
                self.state, self.collector, self.mac, self.ip,
                self.tcp, 1000, self.fake_nmap, "UDP timed out"
            )
        record = load_state(self.state)["profiles"][self.mac]
        self.assertEqual(record["status"], "reserved")
        self.assertNotIn("profile", record)
