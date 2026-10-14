"""Regression tests for the AI management-report summary."""

import importlib.util
import unittest
from pathlib import Path


ROLE = Path(__file__).resolve().parent
AI_FILE = ROLE / "files" / "homelab-management-report-ai.py"


def load_ai():
    spec = importlib.util.spec_from_file_location(
        "homelab_management_report_ai",
        AI_FILE,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ManagementReportAITests(unittest.TestCase):
    def setUp(self):
        self.ai = load_ai()

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
                "name": (
                    "Linux: Operating system description has changed"
                ),
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
                "reporting_hosts": 15,
                "available_hosts": 15,
                "active_problem_count": 6,
                "active_problems": problems,
            },
            "prometheus": {
                "firing_alert_count": 0,
                "firing_alerts": [],
            },
            "alertmanager": {
                "active_alert_count": 0,
                "active_alerts": [],
            },
        }

    def test_information_events_do_not_count_as_ai_conditions(self):
        evidence = self.evidence()

        state = self.ai.management_state(evidence)
        summary = self.ai.safe_summary(evidence)

        self.assertEqual(state["zabbix_problem_count"], 1)
        self.assertEqual(state["monitoring_alert_count"], 0)
        self.assertEqual(state["distinct_condition_count"], 1)

        self.assertNotIn(
            "active_problem_count",
            summary["zabbix"],
        )


if __name__ == "__main__":
    unittest.main()


class ManagementReportAIValidationTests(unittest.TestCase):
    def setUp(self):
        self.ai = load_ai()

    def test_rejects_prometheus_as_host_availability(self):
        with self.assertRaises(ValueError):
            self.ai.validate_briefing(
                "Overall: All hosts are online and fully reporting "
                "across Zabbix, Prometheus, and Loki."
            )

    def test_rejects_unsupported_no_threat_claim(self):
        with self.assertRaises(ValueError):
            self.ai.validate_briefing(
                "Security: No critical threats are detected."
            )

    def test_accepts_evidence_safe_wording(self):
        text = (
            "Overall: Zabbix reports all expected hosts available. "
            "Prometheus telemetry coverage is complete. "
            "Needs attention: One Zabbix condition requires review. "
            "Security: Sensor coverage is complete. "
            "Suggested priority: Review the active condition."
        )

        self.assertEqual(
            self.ai.validate_briefing(text),
            text,
        )
