"""Regression tests: export saved Nmap OS results WITHOUT invoking scans."""
import importlib.util
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = (Path(__file__).resolve().parents[2] /
          "ansible/roles/network_host_deep_profiler/files/"
          "os-fingerprint-evidence-exporter.py")
spec = importlib.util.spec_from_file_location("nmap_os_exporter", SOURCE)
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class FingerprintExporterTests(unittest.TestCase):
    def record(self, **kwargs):
        base = {
            "status": "partial", "profiled_ip": "192.168.2.55",
            "profile": {"tcp_scanned_at": int(time.time()) - 120,
                        "tcp": {"os_matches": [
                            {"name": "Linux 5.X", "accuracy": "96",
                             "classes": [{
                                 "vendor": "Linux", "type": "general purpose",
                                 "os_family": "Linux", "os_generation": "5.X",
                                 "cpe": ["cpe:/o:linux:linux_kernel:5"]}]},
                            {"name": "Linux 4.X", "accuracy": "84",
                             "classes": []}],
                            "ports": [
                                {"state": "open", "port": 22,
                                 "protocol": "tcp", "service": {
                                     "name": "ssh", "product": "OpenSSH",
                                     "version": "9.2"}},
                                {"state": "open|filtered", "port": 161,
                                 "protocol": "udp", "service": {"name": "snmp"}}]}}
        }
        base.update(kwargs)
        return base

    def test_existing_partial_profile_exports_reported_match(self):
        state = {"profiles": {"aa:bb:cc:dd:ee:ff": self.record()}}
        results = exporter.evidence(state)
        self.assertEqual(len(results), 1)
        rec = results[0]
        self.assertEqual(rec["nmap_name"], "Linux 5.X")
        self.assertEqual(rec["nmap_accuracy"], "96%")
        self.assertEqual(rec["nmap_family"], "Linux")
        self.assertEqual(rec["nmap_generation"], "5.X")
        self.assertEqual(rec["nmap_scan_status"], "partial")
        self.assertIn("22/tcp ssh OpenSSH 9.2", rec["nmap_services"])
        self.assertNotIn("snmp", rec["nmap_services"])
        self.assertEqual(rec["profiled_ip"], "192.168.2.55")
        self.assertIn("homelab_network_host_os_fingerprint_info",
                      exporter.render(results))

    def test_no_match_means_no_fingerprint_metric(self):
        state = {"profiles": {"aa:bb:cc:dd:ee:ff": self.record(
            profile={"tcp_scanned_at": int(time.time()) - 120,
                     "tcp": {"os_matches": [], "ports": []}})}}
        self.assertEqual(exporter.evidence(state), [])
        rendered = exporter.render([])
        self.assertNotIn('mac="aa:bb', rendered)

    def test_identity_and_scan_freshness_gates(self):
        now = int(time.time())
        cases = [
            ("bad", self.record()),
            ("aa:bb:cc:dd:ee:ff", self.record(profiled_ip="8.8.8.8")),
            ("aa:bb:cc:dd:ee:ff", self.record(status="pending")),
            ("aa:bb:cc:dd:ee:ff", self.record(profile={
                "tcp_scanned_at": now + 86400,
                "tcp": {"os_matches": [{"name": "Linux", "accuracy": "99"}]}})),
        ]
        for mac, record in cases:
            with self.subTest(mac=mac, status=record.get("status")):
                self.assertEqual(exporter.evidence({
                    "profiles": {mac: record}}), [])

    def test_invalid_state_preserves_last_good_textfile(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td) / "profiles.json"
            out = Path(td) / "last-good.prom"
            state.write_text('{"profiles": []}')
            out.write_text("last-good-data")
            with patch.object(exporter, "STATE", state), \
                 patch.object(exporter, "OUTPUT", out):
                with self.assertRaises(ValueError):
                    exporter.main()
                self.assertEqual(out.read_text(), "last-good-data")

    def test_legacy_profile_completion_date_recovers_existing_matches(self):
        # Existing Proxmox-2 state has OS matches but none of the new
        # profile['tcp_scanned_at'] fields. Do not throw away valid evidence.
        done = int(time.time()) - 3600
        record = self.record(profiled_at=done)
        record["profile"].pop("tcp_scanned_at")
        result = exporter.evidence({
            "profiles": {"aa:bb:cc:dd:ee:ff": record}})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["nmap_name"], "Linux 5.X")
        self.assertEqual(result[0]["scanned"], done)
        self.assertEqual(result[0]["nmap_time_basis"], "Profile completion")
        self.assertIn('nmap_time_basis="Profile completion"',
                      exporter.render(result))

    def test_legacy_nested_scan_timestamp_has_precedence(self):
        done = int(time.time()) - 3600
        record = self.record(profiled_at=done + 120)
        record["profile"].pop("tcp_scanned_at")
        record["profile"]["scanned_at"] = done
        result = exporter.evidence({
            "profiles": {"aa:bb:cc:dd:ee:ff": record}})
        self.assertEqual(result[0]["scanned"], done)
        self.assertEqual(result[0]["nmap_time_basis"], "Legacy scan")

    def test_undated_legacy_match_is_explicit_not_discarded_or_backdated(self):
        record = self.record()
        record["profile"].pop("tcp_scanned_at")
        result = exporter.evidence({
            "profiles": {"aa:bb:cc:dd:ee:ff": record}})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["nmap_scanned_at"], "Not recorded")
        self.assertEqual(result[0]["nmap_time_basis"], "Unknown")
        self.assertIsNone(result[0]["scanned"])
        metrics = exporter.render(result)
        self.assertIn('nmap_scanned_at="Not recorded"', metrics)
        self.assertFalse(any(
            line.startswith("homelab_network_host_os_fingerprint_scan_timestamp_seconds{")
            for line in metrics.splitlines()))

    def test_explicit_invalid_legacy_timestamps_cannot_fake_recency(self):
        record = self.record(profiled_at=int(time.time()) + 86400)
        record["profile"].pop("tcp_scanned_at")
        self.assertEqual(exporter.evidence({
            "profiles": {"aa:bb:cc:dd:ee:ff": record}}), [])
        self.assertFalse(exporter.evidence_time(
            {"tcp_scanned_at": "nonsense"}, {"profiled_at": None})[1])

    def test_recreates_eight_legacy_matches_from_49_record_inventory(self):
        # Regress the observed Proxmox-2 count without copying device IDs.
        now = int(time.time()) - 7200
        records = {}
        for n in range(35):
            records[f"02:00:00:01:00:{n:02x}"] = {"status": "baseline"}
        for n in range(13):
            tcp = {
                "os_matches": (
                    [{"name": "Linux / embedded", "accuracy": "92"}]
                    if n < 8 else []),
                "ports": []}
            records[f"02:00:00:02:00:{n:02x}"] = {
                "status": "complete", "profiled_ip":
                    f"192.168.2.{110+n}",
                "profiled_at": now,
                "profile": {"tcp": tcp},
            }
        records["02:00:00:03:00:00"] = {"status": "pending"}
        results = exporter.evidence({"profiles": records})
        self.assertEqual(len(records), 49)
        self.assertEqual(len(results), 8)
        self.assertTrue(all(r["nmap_time_basis"] == "Profile completion"
                            for r in results))

    def test_no_scan_capability_in_evidence_exporter(self):
        source = SOURCE.read_text()
        self.assertNotIn("subprocess", source)
        self.assertNotIn("os.system(", source)
        self.assertNotIn("socket.connect(", source)


if __name__ == "__main__":
    unittest.main()
