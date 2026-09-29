#!/usr/bin/env python3
"""Offline tests for restricted dual-Pi-hole DNS evidence collection."""

import ast
import json
import sqlite3
import tempfile
import time
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REMOTE = HERE / "templates/homelab-dns-evidence-query.py.j2"
MONITOR = HERE / "templates/homelab-network-dns-evidence.py.j2"


def load_remote_functions(db):
    source = REMOTE.read_text()
    source = source.replace(
        "{{ network_host_dns_evidence_lookback_days }}", "7"
    ).replace(
        "{{ network_host_dns_evidence_max_domains }}", "5"
    )
    tree = ast.parse(source)
    selected = [
        node for node in tree.body
        if (
            isinstance(node, ast.FunctionDef)
            and node.name in {
                "requested_request", "domain_signals", "query_summary"
            }
        ) or (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "SIGNAL_RULES"
                for target in node.targets
            )
        )
    ]
    namespace = {
        "ipaddress": __import__("ipaddress"),
        "json": json,
        "os": __import__("os"),
        "sqlite3": sqlite3,
        "time": time,
        "DB": str(db),
        "LOOKBACK_SECONDS": 7 * 86400,
        "MAX_DOMAINS": 5,
        "LAN": __import__("ipaddress").ip_network("192.168.2.0/24"),
    }
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(REMOTE), "exec"),
         namespace)
    return namespace


def load_monitor_functions():
    source = MONITOR.read_text()
    replacements = {
        "{{ network_host_dns_evidence_profiles }}": "/tmp/profiles.json",
        "{{ network_host_dns_evidence_state }}": "/tmp/dns.json",
        "{{ network_host_dns_evidence_key }}": "/tmp/key",
        "{{ network_host_dns_evidence_known_hosts }}": "/tmp/known_hosts",
        "{{ network_host_dns_evidence_remote_user }}": "dns-evidence",
        "{{ network_host_dns_evidence_failed_retry_seconds }}": "3600",
        "{{ network_host_dns_evidence_servers | to_json }}":
            '[{"name":"dns-01","address":"192.168.2.51"},'
            '{"name":"dns-02","address":"192.168.2.50"}]',
    }
    for old, new in replacements.items():
        source = source.replace(old, new)

    tree = ast.parse(source)
    selected = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name in {"due_for_dns", "correlate", "refresh"}
    ]
    namespace = {
        "FAILED_RETRY_SECONDS": 3600,
        "EVIDENCE_VERSION": 2,
        "SERVERS": [
            {"name": "dns-01", "address": "192.168.2.51"},
            {"name": "dns-02", "address": "192.168.2.50"},
        ],
    }
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(MONITOR), "exec"),
         namespace)
    return namespace


class DnsEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "pihole-FTL.db"
        connection = sqlite3.connect(self.db)
        connection.executescript(
            """
            CREATE TABLE client_by_id (id INTEGER PRIMARY KEY, ip TEXT);
            CREATE TABLE domain_by_id (id INTEGER PRIMARY KEY, domain TEXT);
            CREATE TABLE query_storage (
                id INTEGER PRIMARY KEY,
                timestamp REAL NOT NULL,
                status INTEGER NOT NULL DEFAULT 0,
                domain INTEGER NOT NULL,
                client INTEGER NOT NULL
            );
            INSERT INTO client_by_id VALUES (1, '192.168.2.206');
            INSERT INTO client_by_id VALUES (2, '192.168.2.207');
            INSERT INTO domain_by_id VALUES (1, 'one.example');
            INSERT INTO domain_by_id VALUES (2, 'two.example');
            """
        )
        now = 2_000_000
        connection.executemany(
            "INSERT INTO query_storage(id,timestamp,domain,client) VALUES (?,?,?,?)",
            [
                (1, now - 10, 1, 1),
                (2, now - 20, 1, 1),
                (3, now - 30, 2, 1),
                (4, now - 40, 1, 2),
                (5, now - (8 * 86400), 2, 1),
            ],
        )
        connection.commit()
        connection.close()
        self.now = now

    def test_remote_summary_is_bounded_and_client_specific(self):
        worker = load_remote_functions(self.db)
        summary = worker["query_summary"](
            "192.168.2.206", self.now, self.now
        )
        self.assertEqual(summary["query_count"], 3)
        self.assertEqual(
            summary["top_domains"], ["one.example", "two.example"]
        )
        self.assertLessEqual(len(summary["top_domains"]), 5)
        self.assertEqual(summary["lookback_days"], 7)

    def test_dns_runs_once_after_each_completed_profile(self):
        worker = load_monitor_functions()
        due = worker["due_for_dns"]
        record = {
            "status": "complete",
            "profiled_at": 1000,
        }
        self.assertTrue(due(record, None, 1100))
        self.assertFalse(due(
            record,
            {
                "evidence_version": 2,
                "checked_at": 1000,
                "last_attempt": 1000,
                "error": "",
            },
            1100,
        ))
        self.assertTrue(due(
            {**record, "profiled_at": 2000},
            {
                "evidence_version": 2,
                "checked_at": 1000,
                "last_attempt": 1000,
                "error": "",
            },
            2100,
        ))
        self.assertFalse(due(
            {"status": "partial", "profiled_at": 2000},
            None,
            2100,
        ))

    def test_evidence_version_upgrade_forces_refresh(self):
        worker = load_monitor_functions()
        due = worker["due_for_dns"]
        record = {"status": "complete", "profiled_at": 1000}
        previous = {
            "evidence_version": 1,
            "checked_at": 1000,
            "last_attempt": 1000,
            "error": "",
        }
        self.assertTrue(due(record, previous, 1100))

    def test_fire_tv_signal_and_correlation_are_bounded(self):
        worker = load_remote_functions(self.db)
        connection = sqlite3.connect(self.db)
        connection.execute(
            "INSERT INTO domain_by_id VALUES (3, 'ftvpes-eu.amazon.com')"
        )
        connection.execute(
            "INSERT INTO query_storage(id,timestamp,domain,client) "
            "VALUES (6,?,?,?)",
            (self.now - 5, 3, 1),
        )
        connection.commit()
        connection.close()

        summary = worker["query_summary"](
            "192.168.2.206", self.now, self.now
        )
        ids = {item["id"] for item in summary["signals"]}
        self.assertIn("amazon_fire_tv", ids)
        self.assertLessEqual(len(summary["top_domains"]), 5)
        for signal in summary["signals"]:
            self.assertLessEqual(len(signal["examples"]), 3)

        monitor = load_monitor_functions()
        correlated = monitor["correlate"](
            {
                "vendor": "Amazon Technologies",
                "profile": {
                    "tcp": {
                        "ports": [{
                            "service": {
                                "name": "http",
                                "product": "Amazon FireTV Stick",
                            }
                        }]
                    }
                },
            },
            [{
                "signals": summary["signals"],
            }],
        )
        self.assertEqual(
            correlated["device_hint"],
            "Amazon Fire TV / Fire TV Stick",
        )
        self.assertEqual(correlated["confidence"], "corroborated")

    def test_failed_dns_query_has_one_hour_backoff(self):
        worker = load_monitor_functions()
        due = worker["due_for_dns"]
        record = {
            "status": "complete",
            "profiled_at": 2000,
        }
        previous = {
            "evidence_version": 2,
            "checked_at": 0,
            "last_attempt": 3000,
            "error": "resolver unavailable",
        }
        self.assertFalse(due(record, previous, 6599))
        self.assertTrue(due(record, previous, 6600))

    def test_refresh_queries_both_resolvers_once(self):
        worker = load_monitor_functions()
        calls = []

        def fake_query(server, ip, profiled_at):
            calls.append((server["name"], ip, profiled_at))
            return {
                "server": server["name"],
                "query_count": 1,
                "top_domains": ["service.example"],
                "signals": [],
                "lookback_days": 7,
                "observed_at": 4000,
                "window_start": 0,
                "window_end": 4000,
            }

        refresh = types.FunctionType(
            worker["refresh"].__code__,
            {**worker, "query_server": fake_query},
        )
        profiles = {
            "02:00:00:00:00:42": {
                "status": "complete",
                "profiled_at": 3500,
                "profiled_ip": "192.168.2.206",
                "profile": {"tcp": {"ports": []}},
            }
        }
        state = {"devices": {}}
        count = refresh(profiles, state, 4000)
        self.assertEqual(count, 1)
        self.assertEqual(
            calls,
            [
                ("dns-01", "192.168.2.206", 3500),
                ("dns-02", "192.168.2.206", 3500),
            ],
        )
        entry = state["devices"]["02:00:00:00:00:42"]
        self.assertEqual(entry["checked_at"], 4000)
        self.assertEqual(len(entry["servers"]), 2)
        self.assertEqual(entry["error"], "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
