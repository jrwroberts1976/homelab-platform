#!/usr/bin/env python3
"""Read-only Trivy evidence inventory: show real patch candidates, never invent fixes.

Reads local Docker and validated existing per-image JSON. No scan, file writes,
Docker pull/restart, apt work or network API calls. Prints bounded, sanitised
Critical/High fix-candidate examples and per-image counts only.
"""
import collections
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path("/var/lib/homelab-container-security")
SUMMARY = ROOT / "pilot-inventory-summary.json"
SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN")
MAX_AGE = 30 * 3600

def safe_text(value, limit=95):
    s = " ".join(str(value or "").split())
    return s if len(s) <= limit else s[: limit-1] + "…"

def docker_command(*args):
    return subprocess.check_output(["docker", *args], text=True, timeout=35)

def live_inventory():
    output = docker_command("ps", "--format", "json")
    tags = {json.loads(line)["Image"] for line in output.splitlines() if line.strip()}
    if not tags or len(tags) > 100:
        raise ValueError("Running image inventory empty or outside safety bound")
    ids = {}
    for tag in sorted(tags):
        obj = json.loads(docker_command("image", "inspect", tag))
        if not isinstance(obj, list) or len(obj) != 1:
            raise ValueError("Malformed Docker image inspect result")
        ids[tag] = obj[0]["Id"]
    return ids

def scan_report_rows(report, counts, expected_id):
    if not isinstance(report, dict) or report.get("Metadata", {}).get("ImageID") != expected_id:
        raise ValueError("Trivy report metadata/image ID mismatch")
    sections = report.get("Results", [])
    if not isinstance(sections, list):
        raise ValueError("Malformed Trivy Results list")
    rows = []
    observed = collections.Counter()
    for section in sections:
        if not isinstance(section, dict):
            raise ValueError("Malformed Trivy section")
        vulns = section.get("Vulnerabilities") or []
        if not isinstance(vulns, list):
            raise ValueError("Malformed Trivy vulnerabilities list")
        for v in vulns:
            if not isinstance(v, dict):
                raise ValueError("Malformed Trivy finding")
            sev = str(v.get("Severity") or "UNKNOWN").upper()
            if sev not in SEVERITIES:
                raise ValueError("Unrecognised severity in existing evidence")
            observed[sev] += 1
            if sev in ("CRITICAL", "HIGH"):
                rows.append({
                    "severity": sev,
                    "cve": safe_text(v.get("VulnerabilityID") or "NO-ADVISORY-ID", 80),
                    "package": safe_text(v.get("PkgName") or "unknown", 72),
                    "installed": safe_text(v.get("InstalledVersion") or "unlisted", 75),
                    "fixed": safe_text(v.get("FixedVersion") or "", 75),
                    "title": safe_text(v.get("Title") or "", 95),
                })
    if any(observed[severity] != counts.get(severity) for severity in SEVERITIES):
        raise ValueError("Trivy per-severity report counts differ from scanner summary")
    return rows

def summarise_image(image, image_id, entry, now, root=ROOT):
    if entry.get("status") != "SUCCESS" or entry.get("image_id") != image_id:
        raise ValueError("Image report not SUCCESS or immutable identity changed")
    counts = entry.get("counts")
    if not isinstance(counts, dict) or not all(
        isinstance(counts.get(s), int) and counts[s] >= 0 for s in SEVERITIES
    ):
        raise ValueError("Invalid or missing summary severity counts")
    path = Path(entry.get("report") or "")
    if (path.parent.resolve() != root.resolve() or
        not path.name.startswith("image-") or path.suffix != ".json"):
        raise ValueError("Trivy report outside approved evidence directory")
    report = json.loads(path.read_text())
    rows = scan_report_rows(report, counts, image_id)
    unique_ids = {
        severity: len(set(x["cve"] for x in rows
                          if x["severity"] == severity and x["cve"] != "NO-ADVISORY-ID"))
        for severity in ("CRITICAL", "HIGH")
    }
    fixed = [r for r in rows if r["fixed"]]
    no_fix = [r for r in rows if not r["fixed"]]
    return {
        "image": image, "id": image_id[:22],
        "critical_rows": counts["CRITICAL"], "high_rows": counts["HIGH"],
        "distinct_critical_ids": unique_ids["CRITICAL"],
        "distinct_high_ids": unique_ids["HIGH"],
        "trivy_fix_version_rows": len(fixed),
        "unlisted_fix_rows": len(no_fix),
        "fix_candidates": fixed,
        "unlisted_candidates": no_fix,
    }

def collect(now=None, summary_path=SUMMARY, inventory=None):
    now = int(time.time()) if now is None else now
    summary = json.loads(summary_path.read_text())
    timestamp = int(summary.get("scan_completed") or 0)
    age = now - timestamp
    if not (summary.get("complete") is True and 0 <= age <= MAX_AGE):
        raise ValueError("Scan incomplete/stale; no vulnerability patch list trusted")
    image_ids = live_inventory() if inventory is None else inventory
    entries = {e.get("image"): e for e in summary.get("images", [])
               if isinstance(e, dict)}
    if len(entries) != len(summary.get("images", [])):
        raise ValueError("Malformed/duplicate scan inventory entries")
    results = []
    for image, image_id in sorted(image_ids.items()):
        entry = entries.get(image)
        if entry is None:
            raise ValueError("Missing report for running image " + safe_text(image))
        results.append(summarise_image(image, image_id, entry, now,
                                       root=summary_path.parent))
    return age, results

def output(age, results):
    print("TRIVY_READONLY_VERIFIED images=%d age_hours=%.2f" %
          (len(results), age/3600))
    total_critical = sum(x["critical_rows"] for x in results)
    total_high = sum(x["high_rows"] for x in results)
    print("PACKAGE_ROWS critical=%d high=%d" % (total_critical, total_high))
    for r in sorted(results, key=lambda x: (-x["critical_rows"], -x["high_rows"], x["image"])):
        print("IMAGE %s id=%s CRIT_ROWS=%d HIGH_ROWS=%d CRIT_CVE_IDS=%d HIGH_CVE_IDS=%d "
              "TRIVY_FIXED_ROWS=%d UNLISTED_FIXED_ROWS=%d" %
              (safe_text(r["image"], 120), r["id"], r["critical_rows"], r["high_rows"],
               r["distinct_critical_ids"], r["distinct_high_ids"],
               r["trivy_fix_version_rows"], r["unlisted_fix_rows"]))
    fixed = [(x["image"], f) for x in results for f in x["fix_candidates"]]
    fixed.sort(key=lambda pair: (0 if pair[1]["severity"]=="CRITICAL" else 1,
                                 pair[0], pair[1]["cve"], pair[1]["package"]))
    print("===== TRIVY FIX VERSION LISTED (TOP 24; not vendor-approved upgrades) =====")
    for image, row in fixed[:24]:
        print("FIX_HINT %s | %s | %s | %s | %s -> %s | %s" %
              (safe_text(image,80), row["severity"],row["cve"],row["package"],
               row["installed"],row["fixed"],row["title"]))
    print("MORE_FIX_HINT_ROWS_NOT_DISPLAYED=%d" % max(0,len(fixed)-24))
    unresolved = [(x["image"], f) for x in results for f in x["unlisted_candidates"]
                  if f["severity"]=="CRITICAL"]
    unresolved.sort(key=lambda pair:(pair[0],pair[1]["cve"],pair[1]["package"]))
    print("===== CRITICAL WITH NO FIX VERSION IN TRIVY (TOP 12) =====")
    for image, row in unresolved[:12]:
        print("NO_FIX_LISTED %s | %s | %s | %s | %s" %
              (safe_text(image,80), row["cve"],row["package"],row["installed"],row["title"]))
    print("MORE_CRITICAL_NO_FIX_ROWS_NOT_DISPLAYED=%d" % max(0,len(unresolved)-12))
    print("NEXT: verify vendor image/fixed-version availability before proposing an upgrade")
    print("TRIVY_FIXABILITY_READONLY=PASS")

if __name__ == "__main__":
    try:
        output(*collect())
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print("TRIVY_FIXABILITY_READONLY=FAIL "+safe_text(type(exc).__name__+": "+str(exc),170),
              file=sys.stderr)
        sys.exit(1)
