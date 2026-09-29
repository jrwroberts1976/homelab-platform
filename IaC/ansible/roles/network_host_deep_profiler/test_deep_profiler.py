#!/usr/bin/env python3
"""Offline regression tests for the MAC-keyed network deep profiler."""

import ast
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "templates/homelab-network-host-deep-profiler.py.j2"


def load_functions():
    """Load real worker functions without executing its main loop."""
    tree = ast.parse(TEMPLATE.read_text())
    names = {
        "normalise_mac",
        "baseline_backlog_due_at",
        "scan_retry_seconds",
        "scan_due",
        "tcp_has_os_evidence",
        "merge_scan_evidence",
        "fresh_arp_presence",
        "validate_scan_xml",
        "parse_host",
        "targeted_tcp_arguments",
    }
    selected = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name in names
    ]
    assert {node.name for node in selected} == names

    namespace = {
        "hashlib": __import__("hashlib"),
        "ET": ET,
        "INTERFACE": "offline-test",
        "INITIAL_RETRY_SECONDS": 86400,
        "WEEKLY_RETRY_SECONDS": 604800,
    }
    exec(
        compile(
            ast.Module(body=selected, type_ignores=[]),
            str(TEMPLATE),
            "exec",
        ),
        namespace,
    )
    return namespace


class DeepProfilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worker = load_functions()

    @staticmethod
    def xml(ip="192.168.2.242", state="up",
            finished="success", mac="02:00:00:00:00:42"):
        return (
            '<nmaprun>'
            f'<host><status state="{state}"/>'
            f'<address addr="{ip}" addrtype="ipv4"/>'
            f'<address addr="{mac}" addrtype="mac"/>'
            '<ports><port protocol="tcp" portid="22">'
            '<state state="open"/><service name="ssh"/>'
            '</port></ports></host>'
            f'<runstats><finished exit="{finished}"/></runstats>'
            '</nmaprun>'
        )

    def test_valid_scan_parses_expected_host(self):
        result = self.worker["parse_host"](
            self.xml(), "192.168.2.242"
        )
        self.assertEqual(result["ports"][0]["port"], 22)

    def test_invalid_scan_xml_rejected(self):
        invalid = [
            self.xml(ip="192.168.2.243"),
            self.xml(state="down"),
            self.xml(finished="error"),
            self.xml().replace("<runstats>", "<missing>").replace(
                "</runstats>", "</missing>"
            ),
            "<nmaprun><host>",
            "<invalid/>",
        ]
        for xml in invalid:
            with self.subTest(xml=xml[:70]):
                with self.assertRaises((ValueError, ET.ParseError)):
                    self.worker["validate_scan_xml"](
                        xml, "192.168.2.242"
                    )

    def test_duplicate_target_rejected(self):
        xml = self.xml()
        host = xml.split("<host>", 1)[1].split("</host>", 1)[0]
        xml = xml.replace(
            "</host>",
            "</host><host>" + host + "</host>",
            1,
        )
        with self.assertRaises(ValueError):
            self.worker["validate_scan_xml"](
                xml, "192.168.2.242"
            )

    def test_arp_requires_expected_ip_and_mac(self):
        worker = self.worker
        cases = [
            ("192.168.2.242", "02:00:00:00:00:42", True),
            ("192.168.2.243", "02:00:00:00:00:42", False),
            ("192.168.2.242", "02:00:00:00:00:43", False),
            ("", "02:00:00:00:00:42", False),
            ("192.168.2.242", "", False),
        ]
        for ip, mac, expected in cases:
            with self.subTest(ip=ip, mac=mac):
                namespace = worker.copy()
                calls = []
                namespace["run_nmap"] = lambda *a, **kw: (
                    calls.append(1) or self.xml()
                )
                # Rebind the function to the mocked namespace.
                import types
                function = types.FunctionType(
                    worker["fresh_arp_presence"].__code__,
                    namespace,
                )
                self.assertEqual(
                    function(ip, mac), expected
                )
                if not ip or not mac:
                    self.assertEqual(calls, [])

    def test_targeted_nmap_is_bounded(self):
        args = self.worker["targeted_tcp_arguments"]("192.168.2.242")
        self.assertEqual(args[-1], "192.168.2.242")
        self.assertIn("--top-ports", args)
        self.assertIn("-O", args)
        self.assertIn("--host-timeout", args)
        self.assertNotIn("-p-", args)
        self.assertNotIn("--script", args)
        self.assertNotIn("-sU", args)

    def test_scan_retry_schedule_is_24h_then_weekly(self):
        retry = self.worker["scan_retry_seconds"]
        due = self.worker["scan_due"]

        self.assertEqual(retry({"attempt_count": 0}), 86400)
        self.assertEqual(retry({"attempt_count": 1}), 86400)
        self.assertEqual(retry({"attempt_count": 2}), 604800)
        self.assertEqual(
            retry({"attempt_count": 0, "baseline_backlog": True}),
            604800,
        )

        self.assertTrue(due({}, 100000))
        self.assertFalse(due(
            {"last_attempt": 1000, "attempt_count": 1}, 87399
        ))
        self.assertTrue(due(
            {"last_attempt": 1000, "attempt_count": 1}, 87400
        ))
        self.assertFalse(due(
            {"last_attempt": 1000, "attempt_count": 2}, 605799
        ))
        self.assertTrue(due(
            {"last_attempt": 1000, "attempt_count": 2}, 605800
        ))
        self.assertFalse(due(
            {"last_attempt": 200000, "attempt_count": 1}, 100000
        ))

    def test_baseline_backlog_is_stable_and_spread_within_week(self):
        schedule = self.worker["baseline_backlog_due_at"]
        start = 1_000_000
        first = schedule("02:00:00:00:00:42", start, 604800)
        again = schedule("02:00:00:00:00:42", start, 604800)
        other = schedule("02:00:00:00:00:43", start, 604800)

        self.assertEqual(first, again)
        self.assertGreaterEqual(first, start)
        self.assertLess(first, start + 604800)
        self.assertGreaterEqual(other, start)
        self.assertLess(other, start + 604800)
        self.assertNotEqual(first, other)

    def test_os_evidence_requires_an_nmap_match(self):
        has_os = self.worker["tcp_has_os_evidence"]
        self.assertFalse(has_os({}))
        self.assertFalse(has_os({"os_matches": []}))
        self.assertTrue(has_os({
            "os_matches": [{"name": "Linux 5.x", "accuracy": "95"}]
        }))

    def test_failed_udp_preserves_previous_evidence(self):
        merge = self.worker["merge_scan_evidence"]
        previous = {
            "udp": {"ports": [{"port": 161}]},
            "udp_scanned_at": 100,
        }
        result = merge(
            previous, {"ports": [{"port": 22}]},
            None, "timeout", 200,
        )
        self.assertEqual(result["udp"], previous["udp"])
        self.assertEqual(result["udp_scanned_at"], 100)
        self.assertTrue(result["udp_evidence_stale"])
        self.assertEqual(result["errors"]["udp"], "timeout")

    def test_successful_udp_replaces_old_evidence(self):
        merge = self.worker["merge_scan_evidence"]
        result = merge(
            {"udp": {"ports": [{"port": 161}]}},
            {"ports": [{"port": 22}]},
            {"ports": [{"port": 53}]},
            None,
            200,
        )
        self.assertEqual(result["udp"]["ports"][0]["port"], 53)
        self.assertEqual(result["udp_scanned_at"], 200)
        self.assertFalse(result["udp_evidence_stale"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
