"""Regression tests for factual network-inventory management-report evidence."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from jinja2 import Environment, StrictUndefined


ROLE = Path(__file__).resolve().parent
TEMPLATES = ROLE / "templates"


def render_template(name, substitutions):
    source = (TEMPLATES / name).read_text(encoding="utf-8")

    environment = Environment(undefined=StrictUndefined)
    environment.filters["to_json"] = json.dumps

    return environment.from_string(source).render(**substitutions)


def load_collector():
    rendered = render_template(
        "management-report-collector.py.j2",
        {
            "management_report_prometheus_url": "http://prometheus",
            "management_report_alertmanager_url": "http://alertmanager",
            "management_report_loki_url": "http://loki",
            "management_report_zabbix_url": "http://zabbix",
            "management_report_zabbix_token_file": "/tmp/zabbix-token",
            "management_report_expected_hosts": ["monitor-01"],
            "management_report_patch_freshness_minutes": 90,
            "management_report_evidence_hours": 24,
            "management_report_evidence_file": "/tmp/evidence.json",
            "management_report_greenbone_evidence_file": "/tmp/greenbone.json",
            "management_report_greenbone_freshness_hours": 30,
            "management_report_sensor_evidence_file": "/tmp/sensor.json",
            "management_report_sensor_freshness_minutes": 45,
            "management_report_network_inventory_target": "monitor-01",
            "management_report_network_inventory_textfile":
                "/var/lib/prometheus/node-exporter/homelab_network_hosts.prom",
            "management_report_network_inventory_freshness_minutes": 15,
        },
    )

    namespace = {"__name__": "rendered_collector"}
    exec(compile(rendered, "<rendered collector>", "exec"), namespace)
    return namespace


def load_renderer():
    rendered = render_template(
        "management-report-renderer.py.j2",
        {
            "management_report_evidence_file": "/tmp/evidence.json",
            "management_report_output_directory": "/tmp/reports",
            "management_report_prometheus_url": "http://prometheus",
            "management_report_zabbix_url": "http://zabbix",
            "management_report_alertmanager_url": "http://alertmanager",
            "management_report_loki_url": "http://loki",
        },
    )

    namespace = {"__name__": "rendered_renderer"}
    exec(compile(rendered, "<rendered renderer>", "exec"), namespace)
    return namespace


def prometheus_value(value):
    return [
        {
            "metric": {},
            "value": [1000000, str(value)],
        }
    ]


class NetworkInventoryReportTests(unittest.TestCase):
    def setUp(self):
        self.collector = load_collector()
        self.renderer = load_renderer()

    def raw_network_evidence(
        self,
        inventory=51,
        online=41,
        first_seen=0,
        mtime=1000000,
    ):
        return {
            "network_inventory_total": prometheus_value(inventory),
            "network_online_total": prometheus_value(online),
            "network_first_seen_24h": prometheus_value(first_seen),
            "network_inventory_mtime": prometheus_value(mtime),
        }

    def test_queries_are_scoped_to_authoritative_monitor01(self):
        queries = self.collector["QUERIES"]

        self.assertEqual(
            queries["network_inventory_total"],
            'max(homelab_network_host_inventory_total'
            '{target_name="monitor-01"})',
        )

        self.assertEqual(
            queries["network_online_total"],
            'sum(homelab_network_host_up'
            '{target_name="monitor-01"}) or vector(0)',
        )

        self.assertEqual(
            queries["network_first_seen_24h"],
            'count(homelab_network_host_first_seen_seconds'
            '{target_name="monitor-01"} > time() - 86400) '
            'or vector(0)',
        )

        self.assertEqual(
            queries["network_inventory_mtime"],
            'max(node_textfile_mtime_seconds'
            '{target_name="monitor-01",'
            'file="/var/lib/prometheus/node-exporter/'
            'homelab_network_hosts.prom"})',
        )

        network_queries = " ".join(
            queries[name]
            for name in (
                "network_inventory_total",
                "network_online_total",
                "network_first_seen_24h",
                "network_inventory_mtime",
            )
        )

        self.assertNotIn("enrichment", network_queries)

    def test_fresh_network_inventory_is_verified(self):
        raw = self.raw_network_evidence()

        with patch.object(
            self.collector["time"],
            "time",
            return_value=1000030,
        ):
            evidence = self.collector[
                "network_inventory_evidence"
            ](raw)

        self.assertEqual(evidence["status"], "ok")
        self.assertEqual(evidence["inventory_total"], 51)
        self.assertEqual(evidence["currently_online"], 41)
        self.assertEqual(evidence["first_seen_24h"], 0)
        self.assertEqual(evidence["source_age_seconds"], 30)
        self.assertEqual(
            evidence["freshness_threshold_seconds"],
            900,
        )

        output = "\n".join(
            self.renderer["network_inventory_section"](
                {"network_inventory": evidence}
            )
        )

        self.assertIn("Status: Evidence current", output)
        self.assertIn("Inventory devices: 51", output)
        self.assertIn("Currently online: 41", output)
        self.assertIn(
            "First observed in last 24h: 0",
            output,
        )

    def test_stale_network_inventory_suppresses_counts(self):
        raw = self.raw_network_evidence()

        with patch.object(
            self.collector["time"],
            "time",
            return_value=1001000,
        ):
            evidence = self.collector[
                "network_inventory_evidence"
            ](raw)

        self.assertEqual(evidence["status"], "stale")

        output = "\n".join(
            self.renderer["network_inventory_section"](
                {"network_inventory": evidence}
            )
        )

        self.assertIn("Status: EVIDENCE STALE", output)
        self.assertIn(
            "Network inventory evidence exceeds freshness threshold",
            output,
        )

        # Stale counts must never be presented as verified current facts.
        self.assertNotIn("Inventory devices:", output)
        self.assertNotIn("Currently online:", output)
        self.assertNotIn("First observed in last 24h:", output)
        self.assertNotIn("51", output)
        self.assertNotIn("41", output)

    def test_online_count_cannot_exceed_inventory(self):
        raw = self.raw_network_evidence(
            inventory=51,
            online=82,
        )

        with patch.object(
            self.collector["time"],
            "time",
            return_value=1000030,
        ):
            evidence = self.collector[
                "network_inventory_evidence"
            ](raw)

        self.assertEqual(evidence["status"], "invalid")
        self.assertEqual(
            evidence["reason"],
            "Currently-online count exceeds retained inventory total",
        )

        output = "\n".join(
            self.renderer["network_inventory_section"](
                {"network_inventory": evidence}
            )
        )

        self.assertIn("Status: EVIDENCE INVALID", output)
        self.assertNotIn("Inventory devices:", output)
        self.assertNotIn("Currently online:", output)

    def test_missing_required_metric_is_unavailable(self):
        raw = self.raw_network_evidence()
        raw["network_inventory_mtime"] = []

        evidence = self.collector[
            "network_inventory_evidence"
        ](raw)

        self.assertEqual(evidence["status"], "unavailable")
        self.assertIn(
            "required Prometheus network inventory metrics are absent",
            evidence["reason"],
        )


if __name__ == "__main__":
    unittest.main()
