#!/usr/bin/env python3
"""Isolated regression test: factual provenance is source-derived, not AI-authored."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jinja2 import Environment, StrictUndefined

ROLE = Path(__file__).resolve().parents[2] / "ansible/roles/management_report/templates"


class FactualProvenanceTests(unittest.TestCase):
    def test_source_references_and_missing_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "evidence.json"
            reports = root / "reports"
            evidence.write_text(json.dumps({
                "collected_at": "2026-09-23T05:00:00+00:00",
                "prometheus": {
                    "expected_hosts": 15,
                    "node_exporter_reporting_hosts": 15,
                    "patch_reporting_hosts": 15,
                    "patch_fresh_hosts": 15,
                    "firing_alert_count": 0,
                },
                "zabbix": {"active_problem_count": 0},
                "alertmanager": {"active_alert_count": 0},
                "greenbone": {
                    "status": "stale",
                    "source": "/synthetic/greenbone.json",
                    "collected_at": "2026-09-20T01:00:00+00:00",
                    "report_id": "synthetic-report-id",
                },
            }))
            rendered = Environment(undefined=StrictUndefined).from_string(
                (ROLE / "management-report-renderer.py.j2").read_text()
            ).render(
                management_report_evidence_file=str(evidence),
                management_report_output_directory=str(reports),
                management_report_prometheus_url="http://prometheus.invalid:9090",
                management_report_zabbix_url="http://zabbix.invalid/api_jsonrpc.php",
                management_report_alertmanager_url="http://alertmanager.invalid:9093",
                management_report_loki_url="http://loki.invalid:3100",
            )
            script = root / "renderer.py"
            script.write_text(rendered)
            subprocess.run([sys.executable, str(script)], check=True, capture_output=True)
            report = (reports / "latest.txt").read_text()
            self.assertIn("Verified Evidence Sources", report)
            self.assertIn("Collection timestamp (UTC): 2026-09-23T05:00:00+00:00", report)
            self.assertIn("Prometheus: http://prometheus.invalid:9090", report)
            self.assertIn("Greenbone status: STALE", report)
            self.assertIn("Greenbone evidence: /synthetic/greenbone.json", report)
            self.assertIn("Greenbone report ID: synthetic-report-id", report)
            self.assertIn("Network sensor: NOT ASSESSED (evidence section absent)", report)
            self.assertIn("Security vulnerabilities: evidence STALE", report)
            self.assertNotIn("Security vulnerabilities: 0 actionable", report)
            self.assertNotIn("AI Management Briefing", report)


if __name__ == "__main__":
    unittest.main()
