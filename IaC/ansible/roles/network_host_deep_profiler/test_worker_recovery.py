#!/usr/bin/env python3
"""Offline integration tests for the actual deep-profiler worker."""

import ast
import contextlib
import io
import json
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "templates/homelab-network-host-deep-profiler.py.j2"

MAC = "02:00:00:00:00:42"
OLD_IP = "192.168.2.241"
NEW_IP = "192.168.2.242"


def evidence(port):
    return {
        "os_matches": [],
        "ports": [{"port": port, "state": "open"}],
    }


class WorkerRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)

        root = Path(self.temporary.name)
        self.inventory = root / "inventory.json"
        self.state = root / "state.json"
        self.metrics = root / "metrics.prom"

        self.now = int(time.time())
        self.old_time = self.now - 90000

        source = TEMPLATE.read_text()
        replacements = {
            "{{ network_host_deep_profiler_scan_mode }}": "legacy",
            "{{ network_host_deep_profiler_inventory }}":
                str(self.inventory),
            "{{ network_host_deep_profiler_state }}":
                str(self.state),
            "{{ network_host_deep_profiler_metrics }}":
                str(self.metrics),
            "{{ network_host_deep_profiler_interface }}":
                "offline-test",
            "{{ network_host_deep_profiler_recent_seen_seconds }}":
                "3600",
            "{{ network_host_deep_profiler_max_profiles_per_run }}":
                "1",
            "{{ network_host_deep_profiler_enable_baseline_backlog }}":
                "0",
            "{{ network_host_deep_profiler_enable_baseline_backlog | bool | int }}":
                "0",
            "{{ network_host_deep_profiler_baseline_backlog_spread_seconds }}":
                "604800",
            "{{ network_host_deep_profiler_udp_ports }}":
                "53",
            "{{ network_host_deep_profiler_scripts }}":
                "default",
        }

        for old, new in replacements.items():
            self.assertIn(old, source)
            source = source.replace(old, new)

        tree = ast.parse(source)

        start = next(
            index
            for index, node in enumerate(tree.body)
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "inventory"
                for target in node.targets
            )
        )

        self.definitions = compile(
            ast.Module(
                body=tree.body[:start],
                type_ignores=[],
            ),
            str(TEMPLATE),
            "exec",
        )
        self.worker = compile(
            ast.Module(
                body=tree.body[start:],
                type_ignores=[],
            ),
            str(TEMPLATE),
            "exec",
        )

    def write_inventory(self, ip=NEW_IP):
        self.inventory.write_text(json.dumps({
            ip: {
                "mac": MAC,
                "hostname": "offline-device",
                "last_seen": self.now,
                "first_seen": self.old_time,
            }
        }))

    def write_state(self, status="partial", ip=OLD_IP):
        profile = {
            "tcp": evidence(22),
            "tcp_scanned_at": self.old_time,
            "udp": evidence(161),
            "udp_scanned_at": self.old_time,
            "errors": {"udp": "previous timeout"},
        }

        self.state.write_text(json.dumps({
            "schema_version": 1,
            "initialized_at": self.old_time,
            "profiles": {
                MAC: {
                    "status": status,
                    "discovered_at": self.old_time,
                    "last_attempt": self.old_time,
                    "attempt_count": 1,
                    "last_ip": ip,
                    "last_inventory_seen": self.now,
                    "profiled_ip": ip,
                    "profiled_at": self.old_time,
                    "profile": profile,
                }
            },
        }))

        return profile

    def run_worker(self, tcp=None, udp=None, presence=True, mode="legacy"):
        namespace = {"__name__": "__main__"}
        exec(self.definitions, namespace)
        namespace["NOW"] = self.now
        namespace["SCAN_MODE"] = mode

        calls = {"presence": 0, "tcp": 0, "udp": 0}

        def check_presence(ip, mac):
            calls["presence"] += 1
            self.assertEqual(mac, MAC)
            return presence

        def tcp_scan(ip):
            calls["tcp"] += 1
            if isinstance(tcp, Exception):
                raise tcp
            return tcp if tcp is not None else evidence(443)

        def udp_scan(ip):
            calls["udp"] += 1
            if isinstance(udp, Exception):
                raise udp
            return udp if udp is not None else evidence(53)

        namespace.update({
            "fresh_arp_presence": check_presence,
            "deep_tcp_scan": tcp_scan,
            "deep_udp_scan": udp_scan,
        })

        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            try:
                exec(self.worker, namespace)
            except SystemExit as exc:
                self.assertIn(exc.code, (0, None))

        saved = json.loads(self.state.read_text())
        events = [
            json.loads(line)
            for line in output.getvalue().splitlines()
            if line.startswith("{")
        ]

        return saved, calls, events

    def test_first_run_is_baseline_only(self):
        self.write_inventory()

        saved, calls, events = self.run_worker()

        self.assertEqual(calls, {
            "presence": 0,
            "tcp": 0,
            "udp": 0,
        })
        self.assertEqual(
            saved["profiles"][MAC]["status"],
            "baseline",
        )
        self.assertTrue(any(
            event["event"] == "deep_profile_baseline_created"
            for event in events
        ))

    def test_failed_tcp_preserves_previous_evidence(self):
        self.write_inventory(NEW_IP)
        previous = self.write_state(ip=OLD_IP)

        saved, calls, events = self.run_worker(
            tcp=ValueError("invalid XML"),
        )

        record = saved["profiles"][MAC]

        self.assertEqual(calls, {
            "presence": 1,
            "tcp": 1,
            "udp": 0,
        })
        self.assertEqual(record["profile"], previous)
        self.assertEqual(record["status"], "partial")
        self.assertIn("invalid XML", record["last_error"])
        self.assertEqual(record["attempt_count"], 2)
        self.assertTrue(any(
            event["event"] == "deep_profile_failed"
            for event in events
        ))

    def test_same_ip_retries_udp_only(self):
        self.write_inventory(OLD_IP)
        previous = self.write_state(ip=OLD_IP)

        saved, calls, events = self.run_worker(
            udp=evidence(53),
        )

        record = saved["profiles"][MAC]
        profile = record["profile"]

        self.assertEqual(calls, {
            "presence": 1,
            "tcp": 0,
            "udp": 1,
        })
        self.assertEqual(record["status"], "complete")
        self.assertEqual(profile["tcp"], previous["tcp"])
        self.assertEqual(
            profile["tcp_scanned_at"],
            self.old_time,
        )
        self.assertEqual(profile["udp"], evidence(53))
        self.assertTrue(any(
            event["event"] == "deep_profile_complete"
            for event in events
        ))

    def test_changed_ip_failed_udp_keeps_history(self):
        self.write_inventory(NEW_IP)
        previous = self.write_state(ip=OLD_IP)

        saved, calls, events = self.run_worker(
            tcp=evidence(443),
            udp=RuntimeError("UDP timeout"),
        )

        record = saved["profiles"][MAC]
        profile = record["profile"]

        self.assertEqual(calls, {
            "presence": 1,
            "tcp": 1,
            "udp": 1,
        })
        self.assertEqual(record["status"], "partial")
        self.assertEqual(record["profiled_ip"], NEW_IP)
        self.assertEqual(profile["tcp"], evidence(443))
        self.assertEqual(profile["udp"]["ports"], [])
        self.assertIsNone(profile["udp_scanned_at"])

        history = profile["historical_udp_entries"]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["ip"], OLD_IP)
        self.assertEqual(
            history[0]["evidence"],
            previous["udp"],
        )
        self.assertTrue(any(
            event["event"] == "deep_profile_partial"
            for event in events
        ))

    def test_partial_metrics_include_tcp_not_last_success(self):
        self.write_inventory(NEW_IP)
        self.write_state(ip=OLD_IP)

        saved, calls, events = self.run_worker(
            tcp=evidence(443),
            udp=RuntimeError("UDP timeout"),
        )

        self.assertEqual(saved["profiles"][MAC]["status"], "partial")
        metrics = self.metrics.read_text()

        self.assertIn(
            'homelab_network_host_deep_profile_open_tcp_ports_total'
            '{mac="' + MAC + '",ip="' + NEW_IP + '"} 1',
            metrics,
        )
        self.assertNotIn(
            'homelab_network_host_deep_profile_last_success_seconds'
            '{mac="' + MAC + '"}',
            metrics,
        )

    def test_six_ip_changes_keep_only_five_udp_history_entries(self):
        self.write_inventory(OLD_IP)
        self.write_state(ip=OLD_IP)

        for index in range(6):
            if index:
                # Simulate a partial profile requiring recovery.
                state = json.loads(self.state.read_text())
                state["profiles"][MAC]["status"] = "partial"
                self.state.write_text(json.dumps(state))

            ip = "192.168.2." + str(243 + index)
            self.write_inventory(ip)

            # First retry is due after 24 hours. Once the profile has
            # already been retried, incomplete evidence moves to the weekly
            # cadence. This test is about retaining IP-change history, so
            # advance past whichever cooldown applies.
            state = json.loads(self.state.read_text())
            attempts = int(
                state["profiles"][MAC].get("attempt_count", 0) or 0
            )
            self.now += 90000 if attempts <= 1 else 604900
            self.write_inventory(ip)

            saved, calls, events = self.run_worker()
            record = saved["profiles"][MAC]

            self.assertEqual(calls, {
                "presence": 1,
                "tcp": 1,
                "udp": 1,
            })
            self.assertEqual(record["status"], "complete")
            self.assertEqual(record["profiled_ip"], ip)

            history = record["profile"].get(
                "historical_udp_entries", []
            )
            self.assertEqual(len(history), min(index + 1, 5))
            self.assertNotIn(
                ip,
                [entry["ip"] for entry in history],
            )

        self.assertEqual(
            [entry["ip"] for entry in history],
            [
                "192.168.2.243",
                "192.168.2.244",
                "192.168.2.245",
                "192.168.2.246",
                "192.168.2.247",
            ],
        )

    def test_targeted_mode_retries_missing_os_after_24h_then_weekly(self):
        self.write_inventory()
        self.write_state(status="pending", ip=NEW_IP)

        state = json.loads(self.state.read_text())
        state["profiles"][MAC]["attempt_count"] = 0
        state["profiles"][MAC]["last_attempt"] = self.old_time
        self.state.write_text(json.dumps(state))

        saved, calls, events = self.run_worker(mode="targeted")
        self.assertEqual(calls, {"presence": 1, "tcp": 1, "udp": 0})
        record = saved["profiles"][MAC]
        self.assertEqual(record["status"], "partial")
        self.assertEqual(record["last_error"], "os_evidence_missing")
        self.assertTrue(record["needs_os_identification"])
        self.assertEqual(record["next_retry_after"], self.now + 86400)
        self.assertEqual(record["profile"]["tcp"]["ports"][0]["port"], 443)
        self.assertEqual(record["profile"]["udp"]["ports"], [])

        again, repeated_calls, _ = self.run_worker(mode="targeted")
        self.assertEqual(repeated_calls, {"presence": 0, "tcp": 0, "udp": 0})
        self.assertEqual(again["profiles"][MAC]["attempt_count"], 1)

        self.now += 86400
        self.write_inventory()
        weekly, retry_calls, _ = self.run_worker(mode="targeted")
        self.assertEqual(retry_calls, {"presence": 1, "tcp": 1, "udp": 0})
        record = weekly["profiles"][MAC]
        self.assertEqual(record["status"], "partial")
        self.assertEqual(record["attempt_count"], 2)
        self.assertEqual(record["next_retry_after"], self.now + 604800)

        self.now += 86400
        self.write_inventory()
        too_soon, weekly_calls, _ = self.run_worker(mode="targeted")
        self.assertEqual(weekly_calls, {"presence": 0, "tcp": 0, "udp": 0})
        self.assertEqual(too_soon["profiles"][MAC]["attempt_count"], 2)

    def test_presence_failure_does_not_scan(self):
        self.write_inventory()
        self.write_state(ip=NEW_IP)

        saved, calls, events = self.run_worker(
            presence=False,
        )

        record = saved["profiles"][MAC]

        self.assertEqual(calls, {
            "presence": 1,
            "tcp": 0,
            "udp": 0,
        })
        self.assertEqual(
            record["last_error"],
            "fresh_arp_presence_failed",
        )
        self.assertEqual(record["attempt_count"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
