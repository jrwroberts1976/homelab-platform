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


def host_dashboard(name, host, items, os_info):
    active = [x for x in items if x.get("status") == "0"
              and x.get("state") == "0"
              and x.get("value_type") in ("0", "3")]
    panels = [{
        "id": 1, "type": "text", "title": "Zabbix managed host",
        "gridPos": {"x": 0, "y": 0, "w": 24, "h": 6},
        "options": {"mode": "markdown", "content":
                    "### " + name + "\n\n"
                    + "**Zabbix technical host:** " + host["host"] + "\n\n"
                    + "**Operating system:** " + os_info["os"] + "\n\n"
                    + "**Kernel / architecture:** " + os_info["kernel"] + "\n\n"
                    + "**OS source:** " + os_info["source"] + " (snapshot at last dashboard generation).\n\n"
                    + "**Monitored data:** live Zabbix API / enabled, supported numeric items.\n\n"
                    + "If a panel is absent, the required item is not available on this host."},
    }]
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
    panels.append(problem_panel(host["host"], problems_y))
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
        [os_panel, cpu, agent, problem_panel(regex, 30)],
        "OS inventory, managed-device CPU trends, agent ping and current Zabbix problems",
        ["zabbix", "overview"],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Write dashboards; default is read-only preview")
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
        page, missing = host_dashboard(name, host, items, info)
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
