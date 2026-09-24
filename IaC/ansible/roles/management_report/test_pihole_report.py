#!/usr/bin/env python3
"""Regression tests for the privacy-safe Pi-hole management report section."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock
from jinja2 import Environment, StrictUndefined

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE / "templates"


def load_template(name, substitutions):
    source = (TEMPLATES / name).read_text()
    rendered = Environment(undefined=StrictUndefined).from_string(source).render(**substitutions)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(rendered)
        path = Path(tmp.name)
    try:
        spec = importlib.util.spec_from_file_location("report_under_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        path.unlink()


class PiHoleReportTests(unittest.TestCase):
    def test_renderer_status_and_privacy(self):
        renderer = load_template("management-report-renderer.py.j2", {
            "management_report_evidence_file": "/tmp/evidence.json",
            "management_report_output_directory": "/tmp/reports",
            "management_report_prometheus_url": "http://prometheus",
            "management_report_zabbix_url": "http://zabbix",
            "management_report_alertmanager_url": "http://alertmanager",
            "management_report_loki_url": "http://loki",
        })
        evidence = {"pihole": {
            "status": "partial", "source": "Loki pihole-event streams",
            "collected_at": "2026-09-24T05:00:00+00:00",
            "hosts": {
                "dns-01": {"status": "ok", "events_24h": 185968,
                           "gravity_block_events_24h": 6322},
                "dns-02": {"status": "stale", "events_24h": 43520,
                           "gravity_block_events_24h": 711},
            },
        }}
        output = "\n".join(renderer.pihole_section(evidence))
        self.assertIn("dns-01: OK", output)
        self.assertIn("185968", output)
        self.assertIn("dns-02: STALE", output)
        self.assertNotIn("43520", output)  # stale counts cannot appear verified
        self.assertNotIn("client_ip", output)
        provenance = "\n".join(renderer.evidence_provenance_section(evidence))
        self.assertIn("Pi-hole status: PARTIAL", provenance)


    def test_collector_loki_queries_and_partial_failure(self):
        collector = load_template("management-report-collector.py.j2", {
            "management_report_prometheus_url": "http://prometheus",
            "management_report_alertmanager_url": "http://alertmanager",
            "management_report_loki_url": "http://loki",
            "management_report_zabbix_url": "http://zabbix",
            "management_report_zabbix_token_file": "/tmp/zabbix-token",
            "management_report_expected_hosts": ["dns-01", "dns-02"],
            "management_report_patch_freshness_minutes": 90,
            "management_report_evidence_hours": 24,
            "management_report_evidence_file": "/tmp/evidence.json",
            "management_report_greenbone_evidence_file": "/tmp/greenbone.json",
            "management_report_greenbone_freshness_hours": 30,
            "management_report_sensor_evidence_file": "/tmp/sensor.json",
            "management_report_sensor_freshness_minutes": 45,
        })
        queries = []

        def respond(url, params, timeout):
            query = params["query"]
            queries.append(query)
            if 'hostname="dns-02"' in query:
                raise collector.requests.RequestException("simulated Loki failure")
            value = 6322 if "gravity blocked" in query else 3 if "[15m]" in query else 185968
            response = Mock()
            response.json.return_value = {
                "status": "success",
                "data": {"result": [{"value": [0, str(value)]}]},
            }
            return response

        with patch.object(collector.requests, "get", side_effect=respond):
            result = collector.pihole_evidence()
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["hosts"]["dns-01"]["status"], "ok")
        self.assertEqual(result["hosts"]["dns-01"]["events_24h"], 185968)
        self.assertEqual(result["hosts"]["dns-01"]["gravity_block_events_24h"], 6322)
        self.assertEqual(result["hosts"]["dns-02"]["status"], "unavailable")
        self.assertEqual(len(queries), 4)
        self.assertTrue(all('source="pihole-event"' in q for q in queries))
        self.assertTrue(all('job="pihole"' in q for q in queries))

    def test_missing_evidence(self):
        renderer = load_template("management-report-renderer.py.j2", {
            "management_report_evidence_file": "/tmp/evidence.json",
            "management_report_output_directory": "/tmp/reports",
            "management_report_prometheus_url": "http://prometheus",
            "management_report_zabbix_url": "http://zabbix",
            "management_report_alertmanager_url": "http://alertmanager",
            "management_report_loki_url": "http://loki",
        })
        self.assertIn("EVIDENCE UNAVAILABLE", "\n".join(renderer.pihole_section({})))


if __name__ == "__main__":
    unittest.main()
