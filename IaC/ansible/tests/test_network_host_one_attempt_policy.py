#!/usr/bin/env python3
"""Offline regression tests for the deep profiler's one-Nmap-attempt policy.

Never execute the worker itself: it reads inventory, writes state and can run Nmap.
Only extract and execute two pure guard functions from its Jinja2 template.
"""
import ast
import pathlib
import unittest

TEMPLATE = (
    pathlib.Path(__file__).resolve().parents[1]
    / "roles/network_host_deep_profiler/templates/"
    / "homelab-network-host-deep-profiler.py.j2"
)
SOURCE = TEMPLATE.read_text(encoding="utf-8")


def load_guards(one_attempt):
    start = SOURCE.index("def already_attempted_nmap(record):")
    stop = SOURCE.index("\ndef tcp_has_os_evidence(", start)
    snippet = SOURCE[start:stop]
    tree = ast.parse(snippet)
    assert [n.name for n in tree.body if isinstance(n, ast.FunctionDef)] == [
        "already_attempted_nmap", "scan_due"
    ]
    scope = {
        "ONE_ATTEMPT_PER_HOST": one_attempt,
        "scan_retry_seconds": lambda record: 86400,
    }
    exec(compile(tree, str(TEMPLATE), "exec"), scope)
    return scope["already_attempted_nmap"], scope["scan_due"]


class OneAttemptSafetyTests(unittest.TestCase):
    def test_unattempted_host_is_eligible(self):
        attempted, due = load_guards(True)
        self.assertFalse(attempted({"status": "pending", "attempt_count": 0}))
        self.assertTrue(due({"status": "pending", "attempt_count": 0}, 999999))

    def test_completed_record_never_retries(self):
        _, due = load_guards(True)
        self.assertFalse(due({"status": "complete", "attempt_count": 1,
                              "last_attempt": 1}, 999999999))

    def test_partial_or_failed_record_never_retries(self):
        _, due = load_guards(True)
        for status in ("pending", "partial"):
            with self.subTest(status=status):
                self.assertFalse(due({"status": status, "attempt_count": 1,
                                      "last_attempt": 1}, 999999999))

    def test_crash_after_persist_blocks_retry(self):
        _, due = load_guards(True)
        self.assertFalse(due({"attempt_count": 1}, 999999999))
        self.assertFalse(due({"last_attempt": 1}, 999999999))

    def test_legacy_profiles_without_counters_block_retry(self):
        attempted, due = load_guards(True)
        for record in (
            {"status": "complete"},
            {"status": "partial"},
            {"status": "complete", "profiled_at": 123},
            {"status": "partial", "profiled_ip": "192.168.2.184"},
            {"status": "partial", "profile": {"tcp": {"os_matches": []}}},
        ):
            with self.subTest(record=record):
                self.assertTrue(attempted(record))
                self.assertFalse(due(record, 999999999))

    def test_ip_address_change_does_not_reset_mac_attempt(self):
        _, due = load_guards(True)
        record = {"last_ip": "192.168.2.185", "profiled_ip": "192.168.2.184"}
        self.assertFalse(due(record, 999999999))

    def test_legacy_retry_only_if_explicitly_disabled(self):
        _, due = load_guards(False)
        self.assertTrue(due({"attempt_count": 1, "last_attempt": 1}, 999999999))

    def test_worker_has_pre_scan_persist_and_candidate_filter(self):
        self.assertIn(
            "and (not ONE_ATTEMPT_PER_HOST or not already_attempted_nmap(record))",
            SOURCE,
        )
        self.assertIn("if not scan_due(record, NOW):", SOURCE)
        start = SOURCE.index('    record["last_attempt"] = NOW')
        saved = SOURCE.index("    persist_profiles(state, profiles)", start)
        actual_scan = SOURCE.index("            tcp = deep_tcp_scan(ip)", start)
        self.assertLess(saved, actual_scan)
        self.assertIn("network_host_deep_profiler_one_attempt_per_host",
                      SOURCE)


if __name__ == "__main__":
    unittest.main()
