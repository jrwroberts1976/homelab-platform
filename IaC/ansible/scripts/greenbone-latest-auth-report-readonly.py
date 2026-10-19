#!/usr/bin/env python3
"""Read latest completed authenticated Greenbone report via task last_report."""
import runpy
import sys

TASK_ID = "02b610fc-647a-4fb8-98c3-7763e0425c34"
client = runpy.run_path("/usr/local/sbin/homelab-greenbone-scan", run_name="greenbone_report_reader")
gmp = client["gmp"]

# Direct task lookup avoids get_reports pagination and report/task nesting ambiguity.
root = gmp('<get_tasks task_id="' + TASK_ID + '" details="1"/>', timeout_seconds=120)
tasks = [t for t in root.findall(".//task") if t.get("id") == TASK_ID]
if len(tasks) != 1:
    sys.exit("Expected exactly one authenticated task")
task = tasks[0]
print("TASK_STATUS=" + task.findtext("status", "unknown"), flush=True)
reports = []
for node in task.findall(".//report"):
    rid = node.get("id", "")
    if rid:
        reports.append((node.findtext("scan_end", ""), node.findtext("scan_start", ""), rid))
if not reports:
    # Emit safe metadata to help distinguish task response shape from missing reports.
    print("TASK_CHILD_ELEMENTS=" + ",".join(c.tag for c in task), flush=True)
    sys.exit("No report reference returned within authenticated task")
end, start, report_id = max(reports)
print("LATEST_AUTH_REPORT_ID=" + report_id, flush=True)
print("SCAN_START=" + start, flush=True)
print("SCAN_END=" + end, flush=True)
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
