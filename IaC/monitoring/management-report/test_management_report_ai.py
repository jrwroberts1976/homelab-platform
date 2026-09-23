import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

MODULE = Path(__file__).resolve().parents[0] / "homelab-management-report-ai.py"
spec = importlib.util.spec_from_file_location("briefing", MODULE)
ai = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai)


class BriefingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.evidence = self.base / "evidence.json"
        self.factual = self.base / "factual.txt"
        self.output = self.base / "combined.txt"
        self.key = self.base / "key"
        self.factual.write_text("FACTUAL REPORT: 0 actionable\n")
        self.key.write_text("test-only-key")
        self.evidence.write_text(json.dumps({
            "collected_at": "2026-09-23T05:00:00+00:00",
            "greenbone": {"status": "ok", "actionable_count": 0,
                          "secret": "DO_NOT_SEND"},
            "prometheus": {"expected_hosts": 15, "token": "DO_NOT_SEND"},
        }))

    def run_case(self, generator):
        return ai.build(self.evidence, self.factual, self.output,
                        self.key, "test-model", generator)

    def test_success_and_allowlist(self):
        def generate(summary, key, model):
            self.assertNotIn("DO_NOT_SEND", json.dumps(summary))
            self.assertEqual(summary["greenbone"]["actionable_count"], 0)
            return "No confirmed urgent findings."
        self.assertTrue(self.run_case(generate))
        self.assertIn("AI Management Briefing", self.output.read_text())
        self.assertIn("FACTUAL REPORT", self.output.read_text())

    def test_omitted_sources_are_not_assessed(self):
        summary = ai.safe_summary(json.loads(self.evidence.read_text()))
        self.assertEqual(summary["zabbix"]["assessment"], "not_assessed")
        self.assertEqual(summary["alertmanager"]["assessment"], "not_assessed")
        self.assertEqual(summary["loki"]["assessment"], "not_assessed")
        self.assertEqual(summary["network_sensor"]["assessment"], "not_assessed")
        self.assertEqual(summary["greenbone"]["assessment"], "reported")

    def test_api_failure_falls_back(self):
        def fail(*args):
            raise ai.requests.Timeout("offline")
        self.assertFalse(self.run_case(fail))
        self.assertEqual(self.output.read_text(), self.factual.read_text())

    def test_missing_evidence_falls_back(self):
        self.evidence.unlink()
        self.assertFalse(self.run_case(lambda *args: "unused"))
        self.assertEqual(self.output.read_text(), self.factual.read_text())

    def test_previous_briefing_never_reused(self):
        self.output.write_text("YESTERDAY AI BRIEFING")
        self.assertFalse(self.run_case(lambda *args: ""))
        self.assertEqual(self.output.read_text(), self.factual.read_text())

    def test_incomplete_response_rejected(self):
        with self.assertRaises(ValueError):
            ai.extract_text({"status": "incomplete", "output": []})

    def test_http_payload_store_false(self):
        response = Mock()
        response.json.return_value = {
            "status": "completed", "output": [{
                "type": "message", "role": "assistant",
                "content": [{"type": "output_text", "text": "Briefing."}]
            }]
        }
        post = Mock(return_value=response)
        self.assertEqual(ai.generate({"greenbone": {"status": "ok"}},
                                     "test-key", "test-model", post), "Briefing.")
        self.assertIs(post.call_args.kwargs["json"]["store"], False)
        self.assertEqual(post.call_args.kwargs["timeout"], (5, 20))


if __name__ == "__main__":
    unittest.main()
