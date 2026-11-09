#!/usr/bin/env python3
"""Build Grafana dashboard pages from live, enabled Zabbix 7 items.

- Controlled Ansible/IaC deployment, dry-run unless --apply is supplied.
- Uses the existing protected datasource token and Grafana admin password.
- Never deletes or moves dashboards; refuses to overwrite a foreign dashboard.
- Only hosts in the confirmed running-Zabbix-agent inventory are included.
"""
import argparse
import base64
import hashlib
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

ZABBIX_URL = "https://zabbix.home.jrwroberts.co.uk/api_jsonrpc.php"
GRAFANA_URL = "http://127.0.0.1:3000"
DS = {"type": "alexanderzobnin-zabbix-datasource", "uid": "zabbix"}
INVENTORY = Path("/var/lib/homelab-network-hosts/grafana-managed-zabbix-hosts.json")
DATASOURCE = Path("/opt/monitoring/grafana/provisioning/datasources/zabbix.yml")
GRAFANA_ENV = Path("/opt/monitoring/.env")
MARKER = "homelab-zabbix-generated"


def request(url, payload=None, headers=None, method=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers=headers or {},
        method=method or ("POST" if payload is not None else "GET"),
    )
    with urllib.request.urlopen(req, timeout=30) as reply:
        raw = reply.read(15_000_000)
    return json.loads(raw)


def read_secret_files():
    if not INVENTORY.is_file() or INVENTORY.is_symlink():
        raise RuntimeError("Confirmed Zabbix host inventory missing or unsafe")
    entries = json.loads(INVENTORY.read_text(encoding="utf-8"))
    if not isinstance(entries, list) or not (1 <= len(entries) <= 254):
        raise RuntimeError("Invalid Zabbix inventory")
    hostnames = []
    for rec in entries:
        name = rec.get("name", "")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", name) or name in hostnames:
            raise RuntimeError("Invalid or duplicate inventory hostname")
        hostnames.append(name)
    if not DATASOURCE.is_file() or DATASOURCE.is_symlink():
        raise RuntimeError("Protected Zabbix datasource configuration missing")
    token_lines = re.findall(r"^\s*apiToken:\s*(.*?)\s*$", DATASOURCE.read_text(), flags=re.M)
    if len(token_lines) != 1:
        raise RuntimeError("Zabbix datasource token unavailable")
    token = token_lines[0].strip().strip('"').strip("'")
    if not token:
        raise RuntimeError("Zabbix datasource token empty")
    env_lines = GRAFANA_ENV.read_text().splitlines()
    pwd = [line.split("=", 1)[1] for line in env_lines
           if line.startswith("GF_SECURITY_ADMIN_PASSWORD=")]
    if len(pwd) != 1 or not pwd[0]:
        raise RuntimeError("Grafana admin credential unavailable")
    auth = base64.b64encode(("admin:" + pwd[0]).encode()).decode()
    return hostnames, token, {"Authorization": "Basic " + auth,
                              "Content-Type": "application/json"}


def zabbix_api(token, method, params):
    answer = request(
        ZABBIX_URL,
        {"jsonrpc": "2.0", "method": method, "params": params, "id": 1},
        {"Authorization": "Bearer " + token, "Content-Type": "application/json-rpc"},
    )
    if "error" in answer or "result" not in answer:
        raise RuntimeError("Zabbix API failed for " + method + ": " +
                           str(answer.get("error", "missing result")))
    return answer["result"]


def grafana_api(headers, path, method="GET", body=None, missing_ok=False):
    try:
        return request(GRAFANA_URL + path, body, headers, method)
    except urllib.error.HTTPError as exc:
        if missing_ok and exc.code == 404:
            return None
        raise


def metric_target(host, name):
    return {
        "datasource": DS, "refId": "A", "queryType": "0",
        "group": {"filter": "/.*/"},
        "host": {"filter": host},
        "item": {"filter": "/^" + re.escape(name) + "$/"},
        "itemTag": {"filter": ""},
        "application": {"filter": ""},
        "functions": [],
        "options": {"useTrends": "default", "showDisabledItems": False},
    }


def metric_panel(panel_id, title, host, item, y, unit="short", kind="timeseries"):
    p = {
        "id": panel_id, "type": kind, "title": title,
        "datasource": DS, "gridPos": {"x": 12 * ((panel_id - 2) % 2), "y": y, "w": 12, "h": 8},
        "targets": [metric_target(host, item["name"])],
        "fieldConfig": {"defaults": {"unit": unit}, "overrides": []},
    }
    if kind == "timeseries":
        p["options"] = {
            "legend": {"displayMode": "list", "placement": "bottom"},
            "tooltip": {"mode": "single"},
        }
    return p


def problem_panel(host, y, width=24):
    return {
        "id": 90, "type": "table", "title": "Current Zabbix problems",
        "datasource": DS, "gridPos": {"x": 0, "y": y, "w": width, "h": 8},
        "targets": [{
            "datasource": DS, "refId": "A", "queryType": "5",
            "group": {"filter": "/.*/"}, "host": {"filter": host},
            "showProblems": "problems",
            "options": {
                "minSeverity": 0, "acknowledged": 2, "limit": 100,
                "hostsInMaintenance": False, "useTimeRange": False,
            },
        }],
    }


def pick(items, patterns):
    """Prioritise explicit item keys, not invented/display-only item names."""
    for pattern in patterns:
        for item in items:
            if re.fullmatch(pattern, item["key_"], flags=re.I):
                return item
    return None


METRICS = [
    ("CPU utilization", [r"system\.cpu\.util(?:\[.*\])?"], "percent"),
    ("CPU load", [r"system\.cpu\.load\[percpu,avg1\]", r"system\.cpu\.load\[all,avg1\]"], "short"),
    ("Memory utilisation", [r"vm\.memory\.util", r"vm\.memory\.utilization", r"vm\.memory\.size\[pused\]"], "percent"),
    ("Available memory", [r"vm\.memory\.size\[available\]"], "bytes"),
    ("Root filesystem usage", [r"vfs\.fs\.dependent\.size\[/,pused\]", r"vfs\.fs\.size\[/,pused\]"], "percent"),
    ("Root filesystem free", [r"vfs\.fs\.dependent\.size\[/,free\]", r"vfs\.fs\.size\[/,free\]"], "bytes"),
    ("System uptime", [r"system\.uptime"], "s"),
    ("Zabbix agent availability", [r"agent\.ping"], "short"),
]


def network_items(items, direction):
    matches = [item for item in items
               if re.fullmatch(r"net\.if\." + direction + r"\[[^]]+\]", item["key_"])]
    # Do not guess the primary NIC: show at most two, with the real Zabbix item names.
    return sorted(matches, key=lambda x: x["key_"])[:2]


def dashboard(uid, title, panels, description, tags):
    return {
        "id": None, "uid": uid, "title": title, "tags": [MARKER] + tags,
        "description": description, "schemaVersion": 41, "version": 0,
        "refresh": "1m", "time": {"from": "now-6h", "to": "now"},
        "timezone": "browser", "panels": panels,
    }


def safe_markdown(value, maximum=250):
    """Keep Zabbix data from injecting Markdown into dashboard text."""
    cleaned = re.sub(r"[\r\n\t|\x00-\x1f\x7f]", " ", str(value or ""))
    return cleaned.replace("`", "'").replace("<", "&lt;").replace(">", "&gt;")[:maximum].strip()


def os_details(host, items):
    active = [item for item in items if item.get("status") == "0"
              and item.get("state") == "0"
              and item.get("lastclock") not in ("", "0", None)]
    os_item = pick(active, [r"system\.sw\.os(?:\[(?:short|full|name)\])?"])
    kernel_item = pick(active, [r"system\.uname"])
    inv = host.get("inventory") or {}
    os_name = (os_item or {}).get("lastvalue") or inv.get("os_full") or inv.get("os") or "Unknown — no OS item available"
    kernel = (kernel_item or {}).get("lastvalue") or "Unknown — no kernel item available"
    source = "Zabbix latest item" if os_item else ("Zabbix host inventory" if (inv.get("os_full") or inv.get("os")) else "not reported")
    return {"os": safe_markdown(os_name), "kernel": safe_markdown(kernel), "source": source}


def patch_status_panel(y):
    """Visible but honest status until independently verified patch metrics exist."""
    return {
        "id": 91, "type": "text", "title": "Patching status",
        "gridPos": {"x": 0, "y": y, "w": 24, "h": 6},
        "options": {
            "mode": "markdown",
            "content": (
                "### Unknown — patch telemetry not yet verified\n\n"
                "**Pending updates:** Unknown  |  **Security updates:** Unknown  |  "
                "**Reboot required:** Unknown  |  **Last successful patch:** Unknown\n\n"
                "This dashboard does not yet collect verified package update counts or "
                "patch completion timestamps. Existing installed-package inventory, "
                "Zabbix uptime and ordinary agent availability do **not** prove patch compliance. "
                "No updates or package refreshes have been triggered."
            ),
        },
    }


def admin_patching_live_panel(y, items):
    """Show live Zabbix TEXT history only after a recent valid pilot snapshot."""
    import time
    matches = [i for i in items if i.get("key_") == "homelab.patch.snapshot"]
    if len(matches) != 1:
        return patch_status_panel(y)
    item = matches[0]
    if (item.get("status") != "0" or item.get("state") != "0"
            or item.get("value_type") != "4"):
        return patch_status_panel(y)
    try:
        clock = int(item.get("lastclock") or 0)
        snapshot = json.loads(item.get("lastvalue") or "")
        if not (0 <= time.time() - clock <= 3 * 3600):
            return patch_status_panel(y)
        if (snapshot.get("schema_version") != 1
                or snapshot.get("source") != "cached_apt_no_refresh"
                or snapshot.get("error") is not None
                or type(snapshot.get("pending_updates_cached")) is not int
                or snapshot["pending_updates_cached"] < 0
                or snapshot.get("security_updates") is not None
                or snapshot.get("last_verified_patch_utc") is not None):
            return patch_status_panel(y)
    except (ValueError, TypeError, KeyError, AttributeError):
        return patch_status_panel(y)
    return {
        "id": 91, "type": "stat", "title": "Pending patches — admin-01",
        "description": (
            "Two metrics only: cached pending APT package candidates and pending security "
            "patches. Security patch count remains Unknown until an independently "
            "validated classifier is available. Data comes from Zabbix Text history; "
            "no APT refresh is triggered. A stale or missing snapshot is not compliance."
        ),
        "datasource": DS,
        "gridPos": {"x": 0, "y": y, "w": 12, "h": 6},
        "targets": [{
            "datasource": DS, "refId": "A", "queryType": "2",
            "resultFormat": "table",
            "group": {"filter": "/.*/"},
            "host": {"filter": "admin-01"},
            "item": {"filter": "/^Homelab patch snapshot \\(cached APT JSON\\)$/"},
            "application": {"filter": ""}, "itemTag": {"filter": ""},
            "textFilter": "", "options": {"showDisabledItems": False},
        }],
        "transformations": [
            {
                "id": "extractFields",
                "options": {
                    "source": "Last value",
                    "format": "json",
                    "replace": True,
                    "keepTime": False,
                },
            },
            {
                "id": "organize",
                "options": {
                    "excludeByName": {
                        "schema_version": True,
                        "source": True,
                        "error": True,
                        "apt_index_latest_utc": True,
                        "apt_index_age_hours": True,
                        "reboot_required_flag": True,
                        "last_verified_patch_utc": True,
                        "collected_at": True,
                    },
                    "indexByName": {
                        "pending_updates_cached": 0,
                        "security_updates": 1,
                    },
                    "renameByName": {
                        "pending_updates_cached": "Pending patches (cached)",
                        "security_updates": "Security patches",
                    },
                },
            },
        ],
        "fieldConfig": {
            "defaults": {"unit": "short", "noValue": "Unknown", "decimals": 0},
            "overrides": [
                {
                    "matcher": {"id": "byName", "options": "Security patches"},
                    "properties": [{"id": "mappings", "value": [
                        {"type": "special", "options": {"match": "null",
                          "result": {"text": "Unknown"}}}
                    ]}],
                },
            ],
        },
        "options": {
            "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
            "orientation": "horizontal",
            "textMode": "value_and_name",
            "wideLayout": False,
            "colorMode": "none",
            "graphMode": "none",
            "justifyMode": "center",
            "percentChangeColorMode": "standard",
            "showPercentChange": False,
        },
    }


def admin_known_cves_panel(y, prometheus_ds):
    """Count distinct Greenbone CVE labels; missing/stale evidence is Unknown.

    A zero is deliberately not inferred from an absent host series: the existing
    Greenbone exporter has no explicit per-host scan-coverage metric.
    """
    expr = (
        'count(count by (cve) '
        '(homelab_greenbone_cve_finding_score{hostname="admin-01",cve=~"CVE-.+"}))'
        ' and on() '
        '(count(homelab_greenbone_cve_finding_score{hostname="admin-01",cve=~"CVE-.+"}) > 0)'
        ' and on() '
        '(time() - homelab_greenbone_evidence_timestamp_seconds < 108000)'
        ' and on() '
        '(homelab_greenbone_evidence_timestamp_seconds <= time() + 300)'
    )
    return {
        "id": 92, "type": "stat", "title": "Known CVEs — admin-01",
        "description": (
            "Distinct CVE identifiers from Greenbone's existing managed-host "
            "evidence for admin-01. Requires evidence newer than 30 hours. "
            "A missing host series or stale evidence displays Unknown, not zero. "
            "This is a vulnerability count, not a security patch count."
        ),
        "datasource": prometheus_ds,
        "gridPos": {"x": 12, "y": y, "w": 12, "h": 6},
        "targets": [{
            "refId": "A", "datasource": prometheus_ds, "expr": expr,
            "instant": True, "range": False, "format": "time_series",
        }],
        "fieldConfig": {
            "defaults": {"unit": "short", "decimals": 0, "noValue": "Unknown"},
            "overrides": [],
        },
        "options": {
            "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
            "orientation": "horizontal", "textMode": "value",
            "wideLayout": False, "colorMode": "none", "graphMode": "none",
            "justifyMode": "center",
            "percentChangeColorMode": "standard", "showPercentChange": False,
        },
    }



def admin_cve_details_panel(y, prometheus_ds):
    """Show current Greenbone CVE ID, finding name and severity for admin-01."""
    expr = (
        'max by (cve, finding, severity) '
        '(homelab_greenbone_cve_finding_score{hostname="admin-01",cve=~"CVE-.+"})'
        ' and on() '
        '(time() - homelab_greenbone_evidence_timestamp_seconds < 108000)'
        ' and on() '
        '(homelab_greenbone_evidence_timestamp_seconds <= time() + 300)'
    )
    return {
        "id": 93, "type": "table", "title": "Host security — CVE findings",
        "description": (
            "CVE, Greenbone finding description, severity and CVSS score from the "
            "latest managed-host report. Requires evidence under 30 hours old. "
            "An empty table may also mean no current scan evidence; it does not "
            "prove the host is vulnerability-free. Descriptions are Greenbone "
            "finding names, not full vulnerability advisory text."
        ),
        "datasource": prometheus_ds,
        "gridPos": {"x": 0, "y": y, "w": 24, "h": 5},
        "targets": [{
            "refId": "A", "datasource": prometheus_ds, "expr": expr,
            "instant": True, "range": False, "format": "table",
        }],
        "transformations": [{
            "id": "organize",
            "options": {
                "excludeByName": {
                    "Time": True, "__name__": True, "hostname": True,
                    "finding_id": True, "risk_status": True, "port": True,
                    "Metric": True,
                },
                "indexByName": {
                    "cve": 0, "finding": 1, "severity": 2, "Value": 3,
                },
                "renameByName": {
                    "cve": "CVE", "finding": "Description",
                    "severity": "Severity", "Value": "CVSS",
                },
            },
        }],
        "fieldConfig": {
            "defaults": {"custom": {"align": "auto", "filterable": True}},
            "overrides": [
                {"matcher": {"id": "byName", "options": "CVE"},
                 "properties": [{"id": "custom.width", "value": 180}]},
                {"matcher": {"id": "byName", "options": "Description"},
                 "properties": [{"id": "custom.minWidth", "value": 420},
                                {"id": "custom.cellOptions", "value": {"type": "auto", "wrapText": True}}]},
                {"matcher": {"id": "byName", "options": "Severity"},
                 "properties": [{"id": "custom.width", "value": 130}]},
                {"matcher": {"id": "byName", "options": "CVSS"},
                 "properties": [{"id": "custom.width", "value": 95},
                                {"id": "unit", "value": "none"},
                                {"id": "decimals", "value": 1}]},
            ],
        },
        "options": {"showHeader": True, "cellHeight": "sm"},
    }



ADMIN_ROWS = (
    (100, "Host Overview"),
    (101, "System Performance"),
    (102, "Host Security"),
    (103, "Monitoring & Alerts"),
)


def admin_section_rows(source_panels):
    """Four compact host overview cards; other sections keep their data."""
    by_id = {p["id"]: p for p in source_panels}
    required = {1, 90, 91, 92, 93, 94, 95}
    if len(by_id) != len(source_panels) or not required <= set(by_id):
        raise RuntimeError("Incomplete or duplicated admin-01 panels")
    if set(by_id) & {rid for rid, _ in ADMIN_ROWS}:
        raise RuntimeError("Grafana section row ID collision")
    uptime_matches = [p for p in source_panels if p.get("title") == "System uptime"]
    if len(uptime_matches) != 1:
        raise RuntimeError("Expected one existing Zabbix uptime panel")
    uptime = uptime_matches[0]

    def row(row_id, title, y):
        return {"id": row_id, "type": "row", "title": title, "collapsed": False,
                "gridPos": {"x": 0, "y": y, "w": 24, "h": 1}, "panels": []}

    performance = sorted(
        (p for p in source_panels
         if p["id"] not in required | {uptime["id"]}),
        key=lambda p: (p["gridPos"]["y"], p["gridPos"]["x"]),
    )
    result = [row(100, "Host Overview", 0)]
    for panel_id, x, y in ((1, 4, 1), (94, 12, 1),
                           (95, 4, 3)):
        panel = by_id[panel_id]
        panel["gridPos"].update({"x": x, "y": y, "w": 8, "h": 2})
        result.append(panel)

    uptime["type"] = "stat"
    uptime["gridPos"].update({"x": 12, "y": 3, "w": 8, "h": 2})
    uptime["options"] = {
        "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
        "orientation": "horizontal", "textMode": "value",
        "wideLayout": False, "colorMode": "none", "graphMode": "none",
        "justifyMode": "center",
        "text": {"valueSize": 24},
    }
    result.append(uptime)

    result.append(row(101, "System Performance", 5))
    for i, panel in enumerate(performance):
        panel["gridPos"]["x"] = 12 * (i % 2)
        panel["gridPos"]["y"] = 6 + 8 * (i // 2)
        result.append(panel)
    perf_end = 6 + 8 * ((len(performance) + 1) // 2)

    result.append(row(102, "Host Security", perf_end))
    security_y = perf_end + 1
    for panel_id, offset in ((91, 0), (92, 0), (93, 6)):
        panel = by_id[panel_id]
        panel["gridPos"]["y"] = security_y + offset
        result.append(panel)

    alerts_row_y = security_y + 6 + by_id[93]["gridPos"]["h"]
    result.append(row(103, "Monitoring & Alerts", alerts_row_y))
    problem = by_id[90]
    problem["gridPos"]["y"] = alerts_row_y + 1
    result.append(problem)
    return result


def validate_admin_section_pilot(existing_panels, candidate_panels):
    """Only permit two host cards and rearranging the existing overview."""
    rows = {row_id: title for row_id, title in ADMIN_ROWS}
    old_rows = [p for p in existing_panels if p.get("type") == "row"]
    new_rows = [p for p in candidate_panels if p.get("type") == "row"]
    expected_rows = [(rid, name, False) for rid, name in ADMIN_ROWS]
    if ([(p.get("id"), p.get("title"), p.get("collapsed"))
         for p in old_rows] != expected_rows
            or [(p.get("id"), p.get("title"), p.get("collapsed"))
                for p in new_rows] != expected_rows):
        raise RuntimeError("Unexpected section headers")

    old = {p["id"]: p for p in existing_panels if p.get("type") != "row"}
    new = {p["id"]: p for p in candidate_panels if p.get("type") != "row"}
    if (len(old) != len(existing_panels) - len(old_rows)
            or len(new) != len(candidate_panels) - len(new_rows)
            or set(new) != set(old) | {94, 95}):
        raise RuntimeError("Unexpected panel inventory")

    uptime_ids = [pid for pid, p in old.items()
                  if p.get("title") == "System uptime"]
    if len(uptime_ids) != 1:
        raise RuntimeError("Expected exactly one Zabbix uptime panel")
    uptime_id = uptime_ids[0]

    for panel_id in (94, 95):
        panel = new[panel_id]
        if (panel.get("type") != "text"
                or panel.get("title") != {94: "Operating system",
                                         95: "Kernel"}[panel_id]
                or panel.get("options", {}).get("mode") != "markdown"
                or set(panel.keys()) != {"id", "type", "title",
                                         "gridPos", "options"}):
            raise RuntimeError("Unexpected new overview card")
        if panel_id in old:
            prior = json.loads(json.dumps(old[panel_id]))
            target = json.loads(json.dumps(panel))
            old_grid = prior.pop("gridPos", {})
            new_grid = target.pop("gridPos", {})
            if (prior != target or old_grid.get("y") not in
                    ({94: (1,), 95: (3, 4)}[panel_id])
                    or new_grid.get("y") != {94: 1, 95: 3}[panel_id]
                    or old_grid.get("h") not in (2, 3)
                    or new_grid.get("h") != 2
                    or old_grid.get("w") not in (12, 8)
                    or new_grid.get("w") != 8
                    or old_grid.get("x") not in
                    ({94: (12,), 95: (0, 4)}[panel_id])):
                raise RuntimeError("Existing overview card drift: " + str(panel_id))

    for panel_id, previous_panel in old.items():
        next_panel = new[panel_id]
        previous = json.loads(json.dumps(previous_panel))
        intended = json.loads(json.dumps(next_panel))
        for panel in (previous, intended):
            panel.get("gridPos", {}).pop("y", None)
        if panel_id == 1:
            for panel in (previous, intended):
                panel["gridPos"].pop("x", None)
            if (previous.get("type") != "text" or intended.get("type") != "text"
                    or previous.get("title") not in ("Host summary", "Host")
                    or intended.get("title") != "Host"):
                raise RuntimeError("Unexpected Host panel transition")
            for panel in (previous, intended):
                panel.pop("options", None)
                panel.pop("title", None)
                panel["gridPos"].pop("w", None)
                panel["gridPos"].pop("h", None)
        elif panel_id in (94, 95):
            for panel in (previous, intended):
                panel["gridPos"].pop("x", None)
                panel["gridPos"].pop("w", None)
                panel["gridPos"].pop("h", None)
        elif panel_id == uptime_id:
            if (previous.get("type") != "stat" or intended.get("type") != "stat"
                    or intended.get("datasource") != DS
                    or intended.get("fieldConfig", {}).get("defaults", {}).get("unit") != "s"):
                raise RuntimeError("Live uptime stat changed unexpectedly")
            for panel in (previous, intended):
                panel["gridPos"].pop("x", None)
                panel["gridPos"].pop("w", None)
                panel["gridPos"].pop("h", None)
        if previous != intended:
            raise RuntimeError("Unexpected original panel change: " + str(panel_id))

    for panel_id, x, y in ((1, 4, 1), (94, 12, 1),
                           (95, 4, 3), (uptime_id, 12, 3)):
        if new[panel_id]["gridPos"] != {"x": x, "y": y, "w": 8, "h": 2}:
            raise RuntimeError("Unexpected 2x2 overview dimensions")

    if any(row.get("panels") != [] for row in new_rows):
        raise RuntimeError("Unexpected nested section panels")


def host_dashboard(name, host, items, os_info, prometheus_ds):
    active = [x for x in items if x.get("status") == "0"
              and x.get("state") == "0"
              and x.get("value_type") in ("0", "3")]
    if name == "admin-01":
        kernel_text = os_info["kernel"]
        match = re.search(r"\bLinux\s+\S+\s+(\S+)", kernel_text)
        kernel = safe_markdown(match.group(1), 90) if match else "Unknown"
        match = re.search(r"\b(aarch64|arm64|x86_64|amd64|i386|i686)\b", kernel_text)
        arch = match.group(1) if match else "Unknown"
        # The previous Zabbix OS item exposes a compiler/build string, not an OS release.
        # Debian 13 was verified in the approved 2026-11-08 admin-01 APT pilot.
        overview = "**admin-01**"
    else:
        overview = (
            "### " + name + "\n\n"
            + "**Zabbix technical host:** " + host["host"] + "\n\n"
            + "**Operating system:** " + os_info["os"] + "\n\n"
            + "**Kernel / architecture:** " + os_info["kernel"] + "\n\n"
            + "**OS source:** " + os_info["source"] + " (snapshot at last dashboard generation).\n\n"
            + "**Monitored data:** live Zabbix API / enabled, supported numeric items.\n\n"
            + "If a panel is absent, the required item is not available on this host."
        )
    panels = [{
        "id": 1, "type": "text",
        "title": "Host" if name == "admin-01" else "Zabbix managed host",
        "gridPos": {"x": 0, "y": 0, "w": 24, "h": 6},
        "options": {"mode": "markdown", "content": overview},
    }]
    if name == "admin-01":
        panels.extend([
            {"id": 94, "type": "text", "title": "Operating system",
             "gridPos": {"x": 0, "y": 0, "w": 12, "h": 3},
             "options": {"mode": "markdown",
                         "content": "**Debian 13**  ·  " + arch}},
            {"id": 95, "type": "text", "title": "Kernel",
             "gridPos": {"x": 0, "y": 0, "w": 12, "h": 3},
             "options": {"mode": "markdown",
                         "content": "`" + kernel + "`"}},
        ])
    missing = []
    pid = 2
    for title, patterns, unit in METRICS:
        item = pick(active, patterns)
        if item:
            y = 6 + ((pid - 2) // 2) * 8
            panels.append(metric_panel(pid, title, host["host"], item, y, unit))
            pid += 1
        else:
            missing.append(title)
    for direction, label in (("in", "Network received"), ("out", "Network sent")):
        for item in network_items(active, direction):
            y = 6 + ((pid - 2) // 2) * 8
            panels.append(metric_panel(pid, label + " — " + item["name"],
                                       host["host"], item, y, "Bps"))
            pid += 1
    problems_y = 6 + ((pid - 1) // 2) * 8
    if name == "admin-01":
        panels.append(admin_patching_live_panel(problems_y, items))
        panels.append(admin_known_cves_panel(problems_y, prometheus_ds))
        panels.append(admin_cve_details_panel(problems_y + 6, prometheus_ds))
        panels.append(problem_panel(host["host"], problems_y + 11))
    else:
        panels.append(patch_status_panel(problems_y))
        panels.append(problem_panel(host["host"], problems_y + 6))
    if name == "admin-01":
        panels = admin_section_rows(panels)
    uid = "zbx-host-" + hashlib.sha256(name.encode()).hexdigest()[:20]
    return dashboard(uid, name, panels, "Live Zabbix 7 operational metrics for " + name,
                     ["managed-devices", "zabbix"]), missing


def overview_dashboard(host_names, os_inventory):
    names = sorted(host_names)
    regex = "/^(" + "|".join(re.escape(n) for n in names) + ")$/"
    cpu_item = {"name": "CPU utilization"}
    ping_item = {"name": "Zabbix agent ping"}
    cpu = metric_panel(2, "CPU utilisation by host", regex, cpu_item, 0, "percent")
    cpu["gridPos"] = {"x": 0, "y": 0, "w": 24, "h": 10}
    agent = metric_panel(3, "Agent ping by host (where available)", regex, ping_item, 10)
    agent["gridPos"] = {"x": 0, "y": 10, "w": 24, "h": 8}
    rows = ["| Managed host | Operating system | Kernel / architecture |",
            "|---|---|---|"]
    for name in sorted(os_inventory):
        info = os_inventory[name]
        rows.append("| " + safe_markdown(name, 80) + " | " + info["os"]
                    + " | " + info["kernel"] + " |")
    os_panel = {
        "id": 1, "type": "text", "title": "Operating systems — Zabbix inventory",
        "gridPos": {"x": 0, "y": 0, "w": 24, "h": 12},
        "options": {"mode": "markdown",
                    "content": "Latest Zabbix OS information at dashboard generation; missing fields are **Unknown**.\n\n"
                               + "\n".join(rows)},
    }
    cpu["gridPos"]["y"] = 12
    agent["gridPos"]["y"] = 22
    return dashboard(
        "homelab-zabbix-overview", "Homelab — Zabbix Overview",
        [os_panel, cpu, agent, {
            "id": 91, "type": "text", "title": "Patching coverage — managed hosts",
            "gridPos": {"x": 0, "y": 30, "w": 24, "h": 6},
            "options": {
                "mode": "markdown",
                "content": (
                    "**Verified patch compliance:** Unknown on all 15 managed hosts.\n\n"
                    "**Pending/security updates, reboot-required and last-patched:** "
                    "Not currently verified by Zabbix telemetry. "
                    "Do not interpret unknown as zero outstanding updates."
                ),
            },
        }, problem_panel(regex, 36)],
        "OS inventory, managed-device CPU trends, patch coverage status, agent ping and Zabbix problems",
        ["zabbix", "overview"],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Write dashboards; default is read-only preview")
    parser.add_argument("--patch-pilot", action="store_true",
                        help="Refuse all dashboard writes except the admin-01 patch panel")
    args = parser.parse_args()
    names, token, graf_headers = read_secret_files()

    folder = grafana_api(graf_headers, "/api/folders/homelab-managed-devices")
    if folder.get("parentUid") != "homelab-devices":
        raise RuntimeError("Unexpected Managed Devices parent folder")
    root = grafana_api(graf_headers, "/api/folders/homelab")
    if root.get("title") != "Homelab":
        raise RuntimeError("Homelab root folder mismatch")
    source = grafana_api(graf_headers, "/api/datasources/uid/zabbix")
    if source.get("type") != DS["type"]:
        raise RuntimeError("Grafana Zabbix datasource missing")

    # Resolve the already provisioned Prometheus datasource; do not assume its UID.
    data_sources = grafana_api(graf_headers, "/api/datasources")
    prom_sources = [d for d in data_sources if d.get("type") == "prometheus"
                    and d.get("isDefault") is True and d.get("uid")]
    if len(prom_sources) != 1:
        raise RuntimeError("Expected exactly one default Prometheus datasource")
    prometheus_ds = {"type": "prometheus", "uid": prom_sources[0]["uid"]}

    zbx_hosts = zabbix_api(token, "host.get", {
        "output": ["hostid", "host", "name", "status"],
        "selectInventory": ["os", "os_full"],
        "selectParentTemplates": ["templateid", "host"],
        "filter": {"status": "0"},
        "limit": 1000,
    })
    found = {}
    for name in names:
        matches = [h for h in zbx_hosts if name in (h["host"], h["name"])]
        if len(matches) != 1:
            print("SKIP: " + name + " (not uniquely present among enabled Zabbix hosts)")
            continue
        found[name] = matches[0]
    if len(found) != len(names) or len(names) != 15:
        raise RuntimeError("Expected exactly 15 verified Zabbix hosts; refusing incomplete Grafana build")

    # Never build pages from a mixture of legacy and standard host templates.
    standard = zabbix_api(token, "template.get", {
        "filter": {"host": ["Linux by Zabbix agent active"]},
        "output": ["templateid", "host"],
    })
    if len(standard) != 1:
        raise RuntimeError("Standard active Linux template not uniquely present")
    standard_id = standard[0]["templateid"]
    for name, host in found.items():
        linked = host.get("parentTemplates") or []
        if {t["templateid"] for t in linked} != {standard_id}:
            raise RuntimeError("Nonstandard Zabbix template assignment on " + name)
    print("TEMPLATE AUDIT: all 15 managed hosts use only Linux by Zabbix agent active")

    candidates = []
    os_inventory = {}
    host_pages = []
    for name, host in sorted(found.items()):
        items = zabbix_api(token, "item.get", {
            "hostids": host["hostid"], "output": [
                "itemid", "name", "key_", "status", "state", "value_type",
                "lastvalue", "lastclock"
            ], "limit": 10000,
        })
        info = os_details(host, items)
        os_inventory[name] = info
        page, missing = host_dashboard(name, host, items, info, prometheus_ds)
        host_pages.append((page, "homelab-managed-devices"))
        print("HOST: " + name + " panels=" + str(len(page["panels"]))
              + " missing=" + (", ".join(missing) if missing else "none"))

    candidates = [(overview_dashboard([h["host"] for h in found.values()], os_inventory), "homelab")] + host_pages

    # Verify all existing UIDs before the first write.
    actions = []
    for page, folder_uid in candidates:
        prior = grafana_api(graf_headers, "/api/dashboards/uid/" + page["uid"], missing_ok=True)
        if prior is not None:
            old = prior["dashboard"]
            if MARKER not in old.get("tags", []) or prior.get("meta", {}).get("folderUid") != folder_uid:
                raise RuntimeError("Refusing to replace non-generator dashboard " + page["uid"])
            page["id"] = old["id"]
            page["version"] = old["version"]
            if old.get("panels") == page["panels"] and old.get("title") == page["title"]:
                actions.append(("EXISTS", page, folder_uid))
                continue
        actions.append(("UPDATE" if prior else "CREATE", page, folder_uid))

    if args.patch_pilot:
        expected = "admin-01"
        for action, page, _ in actions:
            if page["title"] != expected and action != "EXISTS":
                raise RuntimeError("Pilot refuses unrelated dashboard change: "
                                   + page["title"] + " (" + action + ")")
            if page["title"] == expected and action == "CREATE":
                raise RuntimeError("Pilot refuses creating a replacement admin-01 dashboard")
        admin_action = next((a for a in actions if a[1]["title"] == expected), None)
        if admin_action is None:
            raise RuntimeError("Missing admin-01 dashboard in pilot")
        if not any(p.get("id") == 91 and p.get("type") == "stat"
                   for p in admin_action[1]["panels"]):
            raise RuntimeError("No verified live admin-01 patch table; no changes")
        existing = grafana_api(
            graf_headers, "/api/dashboards/uid/" + admin_action[1]["uid"])
        validate_admin_section_pilot(
            existing["dashboard"]["panels"], admin_action[1]["panels"])
        print("SECTION PILOT GUARD: admin-01 only; all panel data/config unchanged; other 15 dashboards unchanged")
        actions = [admin_action]

    for action, page, folder_uid in actions:
        if args.apply and action != "EXISTS":
            grafana_api(graf_headers, "/api/dashboards/db", "POST", {
                "dashboard": page, "folderUid": folder_uid,
                "overwrite": action == "UPDATE",
                "message": "Reconcile Zabbix-first dashboards from verified items",
            })
        print(("APPLIED " if args.apply else "PLANNED ") + action + ": " + page["title"])
    print("SUMMARY: " + str(len(found)) + " matched Zabbix hosts; "
          + str(len(candidates)) + " candidate dashboards")


if __name__ == "__main__":
    main()
