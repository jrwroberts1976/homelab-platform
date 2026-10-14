"""Regression tests for actionable Zabbix management-report problems."""

import json
import unittest
from pathlib import Path

from jinja2 import Environment, StrictUndefined


ROLE = Path(__file__).resolve().parent
TEMPLATES = ROLE / "templates"


def render_template(name, substitutions):
    source = (TEMPLATES / name).read_text(encoding="utf-8")

    environment = Environment(undefined=StrictUndefined)
    environment.filters["to_json"] = json.dumps

    return environment.from_string(source).render(**substitutions)


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
    exec(
        compile(rendered, "<rendered renderer>", "exec"),
        namespace,
    )
    return namespace


class ZabbixAttentionReportTests(unittest.TestCase):
    def setUp(self):
        self.renderer = load_renderer()

    def evidence(self):
        informational_hosts = [
            "zabbix-01",
            "mail-relay-01",
            "komodo-01",
            "dns-02",
            "PROXMOX",
        ]

        problems = [
            {
                "hosts": [host],
                "name": "Linux: Operating system description has changed",
                "severity": "1",
            }
            for host in informational_hosts
        ]

        problems.append(
            {
                "hosts": ["media-01"],
                "name": "Linux: Interface wlan0: Link down",
                "severity": "3",
            }
        )

        return {
            "zabbix": {
                "expected_hosts": 15,
                "available_hosts": 15,
                "active_problem_count": 6,
                "active_problems": problems,
            },
            "prometheus": {
                "patch_reporting_hosts": 15,
                "patch_fresh_hosts": 15,
                "firing_alert_count": 0,
                "firing_alerts": [],
            },
            "greenbone": {
                "status": "ok",
                "actionable_count": 44,
            },
        }

    def test_information_events_are_not_management_faults(self):
        data = self.evidence()

        summary = "\n".join(
            self.renderer["management_summary"](data)
        )

        attention = "\n".join(
            self.renderer["attention_section"](data)
        )

        self.assertIn(
            "Active infrastructure problems/alerts: 1",
            summary,
        )

        self.assertIn(
            "media-01 - Linux: Interface wlan0: Link down (Average)",
            attention,
        )

        self.assertNotIn(
            "Operating system description has changed",
            attention,
        )

    def test_raw_monitoring_count_is_retained(self):
        data = self.evidence()

        monitoring = "\n".join(
            self.renderer["monitoring_section"](data)
        )

        self.assertIn(
            "Zabbix active problems (all severities): 6",
            monitoring,
        )


if __name__ == "__main__":
    unittest.main()
