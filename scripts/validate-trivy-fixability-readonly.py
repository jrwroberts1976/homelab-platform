#!/usr/bin/env python3
"""Offline evidence-only regression test for five-host Trivy fixability probe."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "IaC/ansible/playbooks/files/trivy-fixability-readonly.py"
PLAY = ROOT / "IaC/ansible/playbooks/trivy-fixability-readonly.yml"

def require_value_error(fn, msg):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError(msg)

def main():
    mod_spec = importlib.util.spec_from_file_location("trivy_fixability", SCRIPT)
    module = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(module)
    now = 1793030000
    image = "ghcr.io/example/container:1.2.3"
    image_id = "sha256:verified-instance"
    with tempfile.TemporaryDirectory(prefix="fixability-test-") as temp:
        root = Path(temp)
        report_path = root / "image-test.json"
        summary_path = root / "pilot-inventory-summary.json"
        report = {
            "Metadata": {"ImageID": image_id},
            "Results": [{"Vulnerabilities": [
                {"Severity": "CRITICAL", "VulnerabilityID": "CVE-2026-12345",
                 "PkgName": "libexample", "InstalledVersion": "1.0",
                 "FixedVersion": "1.1", "Title": "Example fixed issue"},
                {"Severity": "HIGH", "VulnerabilityID": "CVE-2026-23456",
                 "PkgName": "openssl", "InstalledVersion": "2.0",
                 "FixedVersion": "", "Title": "Example unresolved"},
                {"Severity": "LOW", "VulnerabilityID": "CVE-2026-34567",
                 "PkgName": "other", "InstalledVersion": "3.0"},
            ]}]
        }
        summary = {
            "complete": True, "scan_completed": now, "images": [{
                "image": image, "image_id": image_id, "status": "SUCCESS",
                "report": str(report_path),
                "counts": {"CRITICAL": 1,"HIGH": 1,"MEDIUM": 0,"LOW": 1,"UNKNOWN": 0}
            }]
        }
        report_path.write_text(json.dumps(report))
        summary_path.write_text(json.dumps(summary))
        age, images = module.collect(now=now, summary_path=summary_path,
                                     inventory={image: image_id})
        assert age == 0 and len(images) == 1
        assert images[0]["critical_rows"] == 1 and images[0]["high_rows"] == 1
        assert images[0]["trivy_fix_version_rows"] == 1
        assert images[0]["unlisted_fix_rows"] == 1
        assert images[0]["fix_candidates"][0]["fixed"] == "1.1"
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            module.output(age, images)
        assert "TRIVY_FIXABILITY_READONLY=PASS" in out.getvalue()
        assert "FIX_HINT" in out.getvalue() and "NO_FIX_LISTED" not in out.getvalue()

        summary["images"][0]["counts"]["CRITICAL"] = 2
        summary_path.write_text(json.dumps(summary))
        require_value_error(
            lambda: module.collect(now=now,summary_path=summary_path,inventory={image:image_id}),
            "Count mismatch treated as safe")
        summary["images"][0]["counts"]["CRITICAL"] = 1
        summary["scan_completed"] = now-31*3600
        summary_path.write_text(json.dumps(summary))
        require_value_error(
            lambda: module.collect(now=now,summary_path=summary_path,inventory={image:image_id}),
            "Stale scan treated as actionable")
        summary["scan_completed"] = now
        summary_path.write_text(json.dumps(summary))
        require_value_error(
            lambda: module.collect(now=now,summary_path=summary_path,inventory={image:"sha256:changed"}),
            "Image ID drift treated as actionable")
        summary["images"][0]["report"] = "/tmp/not-authorized.json"
        summary_path.write_text(json.dumps(summary))
        require_value_error(
            lambda: module.collect(now=now,summary_path=summary_path,inventory={image:image_id}),
            "Report path escape accepted")
    play = PLAY.read_text()
    for expected in ("serial: 1", "become: true", "changed_when: false",
                     "TRIVY_FIXABILITY_READONLY=PASS", "greenbone-01", "cloud-01"):
        assert expected in play, expected
    forbidden = ("docker pull", "apt upgrade", "systemctl start", "docker compose up",
                 "ansible.builtin.apt", "ansible.builtin.file:")
    assert all(x not in play for x in forbidden)
    print("PASS: read-only Trivy fixability, count/digest/freshness guards")

if __name__ == "__main__":
    main()
