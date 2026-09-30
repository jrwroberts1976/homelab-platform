#!/usr/bin/env python3
"""Regression tests for Greenbone CVE extraction from GMP report XML."""

import types
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "templates/homelab-greenbone-scan.py.j2"


def load_parser():
    source = TEMPLATE.read_text(encoding="utf-8")
    start = source.index("def severity_name(")
    end = source.index("\nACCEPTED_RISKS = {", start)
    selected = source[start:end]
    namespace = {"ET": ET}
    exec(compile(selected, str(TEMPLATE), "exec"), namespace)
    return types.SimpleNamespace(**namespace)


class GreenboneCveTests(unittest.TestCase):
    def setUp(self):
        self.worker = load_parser()

    def parse(self, refs):
        refs_xml = "".join(
            f'<ref type="{ref_type}" id="{ref_id}"/>'
            for ref_type, ref_id in refs
        )
        report = ET.fromstring(
            "<report><results><result>"
            "<host>192.168.2.10</host>"
            "<port>443/tcp</port>"
            "<severity>7.5</severity>"
            "<name>Example finding</name>"
            "<nvt oid=\"1.3.6.1.4.1.example\"><refs>"
            + refs_xml +
            "</refs></nvt>"
            "</result></results></report>"
        )
        return self.worker.parse_results(report)[0]

    def test_single_cve_is_exported(self):
        finding = self.parse([("cve", "CVE-2026-1234")])
        self.assertEqual(finding["cves"], ["CVE-2026-1234"])

    def test_multiple_cves_are_exported_and_deduplicated(self):
        finding = self.parse([
            ("cve", "CVE-2026-1234"),
            ("CVE", "cve-2026-5678"),
            ("cve", "CVE-2026-1234"),
        ])
        self.assertEqual(
            finding["cves"],
            ["CVE-2026-1234", "CVE-2026-5678"],
        )

    def test_non_cve_references_are_ignored(self):
        finding = self.parse([
            ("url", "https://example.invalid"),
            ("bid", "123"),
            ("cve", "CVE-2026-9999"),
        ])
        self.assertEqual(finding["cves"], ["CVE-2026-9999"])

    def test_finding_without_cves_remains_valid(self):
        finding = self.parse([])
        self.assertEqual(finding["cves"], [])
        self.assertEqual(finding["oid"], "1.3.6.1.4.1.example")
        self.assertEqual(finding["severity"], "High")

    def test_cve_output_is_bounded(self):
        finding = self.parse([
            ("cve", f"CVE-2026-{1000 + number}")
            for number in range(30)
        ])
        self.assertEqual(len(finding["cves"]), 20)


if __name__ == "__main__":
    unittest.main(verbosity=2)
