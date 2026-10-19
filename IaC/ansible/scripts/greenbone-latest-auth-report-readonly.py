#!/usr/bin/env python3
"""Read newest completed authenticated Greenbone report directly via existing GMP runner."""
from datetime import datetime
import runpy
import sys

TASK_ID = "02b610fc-647a-4fb8-98c3-7763e0425c34"
client = runpy.run_path("/usr/local/sbin/homelab-greenbone-scan", run_name="greenbone_report_reader")
gmp = client["gmp"]
root = gmp('<get_reports details="0" filter="rows=-1"/>', timeout_seconds=120)
reports = []
for item in root.findall(".//report"):
    task = item.find("task")
    if task is None or task.get("id") != TASK_ID:
        continue
    scan_end = (item.findtext("scan_end") or "").strip()
    if not scan_end:
        continue
    reports.append((scan_end, item.get("id", ""), item.findtext("scan_start", "")))
if not reports:
    sys.exit("No completed authenticated reports returned by GMP")
end, report_id, start = max(reports)
print("LATEST_AUTH_REPORT_ID=" + report_id)
print("SCAN_START=" + start)
print("SCAN_END=" + end)
report = client["get_report"](report_id)
findings = client["parse_results"](report)
nonlog = [x for x in findings if x["severity"] != "Log"]
icmp = [x for x in findings if "icmp timestamp" in x["name"].lower()]
print("TOTAL_NONLOG_FINDINGS=" + str(len(nonlog)))
print("ICMP_TIMESTAMP_COUNT=" + str(len(icmp)))
for x in sorted(nonlog, key=lambda x: (-x["score"], x["host"])):
    print("FINDING host={host} severity={severity} score={score} oid={oid} name={name} cves={cves}".format(
        host=x["host"], severity=x["severity"], score=x["score"], oid=x["oid"],
        name=x["name"], cves=",".join(x["cves"]) or "none"))
