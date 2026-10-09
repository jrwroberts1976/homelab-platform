#!/usr/bin/env python3

import re
import unittest
from pathlib import Path


TEMPLATE = Path(
    __file__
).parents[2] / (
    "ansible/roles/network_host_ai_resolver/templates/"
    "homelab-network-host-ai-resolver.py.j2"
)


def load_policy():
    source = TEMPLATE.read_text()

    match = re.search(
        r"def enforce_manual_review_policy\(result, evidence\):\n"
        r".*?"
        r"(?=\n\ndef ask_model)",
        source,
        re.S,
    )

    if not match:
        raise RuntimeError(
            "Could not extract enforce_manual_review_policy from template"
        )

    namespace = {}
    exec(match.group(0), namespace)
    return namespace["enforce_manual_review_policy"]


class ManualReviewPolicyTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.policy = staticmethod(load_policy())

    def test_high_identity_unknown_os_does_not_require_review(self):
        result = {
            "identity_confidence": "high",
            "os_confidence": "low",
            "exact_os": "",
            "manual_review_required": True,
        }

        actual = self.policy(
            result,
            {"canonical_estate": {}},
        )

        self.assertFalse(actual["manual_review_required"])

    def test_medium_identity_requires_review(self):
        result = {
            "identity_confidence": "medium",
            "os_confidence": "low",
            "manual_review_required": False,
        }

        actual = self.policy(
            result,
            {"canonical_estate": {}},
        )

        self.assertTrue(actual["manual_review_required"])

    def test_low_identity_requires_review(self):
        result = {
            "identity_confidence": "low",
            "os_confidence": "low",
            "manual_review_required": False,
        }

        actual = self.policy(
            result,
            {"canonical_estate": {}},
        )

        self.assertTrue(actual["manual_review_required"])

    def test_canonical_identity_does_not_require_review(self):
        result = {
            "identity_confidence": "medium",
            "os_confidence": "low",
            "manual_review_required": True,
        }

        evidence = {
            "canonical_estate": {
                "name": "hp-switch",
                "kind": "managed switch",
                "role": "core switch",
            }
        }

        actual = self.policy(result, evidence)

        self.assertFalse(actual["manual_review_required"])

    def test_template_normalizes_stored_results_before_weekly_skip(self):
        source = TEMPLATE.read_text()

        normalize_pos = source.index(
            "normalized_result = enforce_manual_review_policy("
        )
        retry_pos = source.index(
            "if prior_time > 0 and NOW - prior_time < RETRY_SECONDS:"
        )

        self.assertLess(normalize_pos, retry_pos)


    def test_policy_does_not_mutate_model_result(self):
        result = {
            "identity_confidence": "high",
            "manual_review_required": True,
        }

        actual = self.policy(
            result,
            {"canonical_estate": {}},
        )

        self.assertTrue(result["manual_review_required"])
        self.assertFalse(actual["manual_review_required"])


if __name__ == "__main__":
    unittest.main()
