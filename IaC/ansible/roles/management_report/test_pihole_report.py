#!/usr/bin/env python3
"""Regression tests for the privacy-safe Pi-hole management report section."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
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
