#!/usr/bin/env python3
"""Guarded presentation-only patch/CPU telemetry migration for 11 managed dashboards.

Default: Grafana/Zabbix API GET only. --apply writes only verified dashboard changes.
Never writes host agents, Zabbix items, router, pilot dashboards or overview.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
import time
from importlib.machinery import SourceFileLoader
from pathlib import Path

BUILDER = Path("/usr/local/sbin/homelab-grafana-zabbix-rebuild")
TARGETS = (
    "PROXMOX", "Proxmox-2", "cloud-01", "dns-02", "edge-01",
    "greenbone-01", "komodo-01", "mail-relay-01", "monitor-01",
    "sensor-01", "zabbix-01",
)
TEMPERATURE = {
    "PROXMOX": "52892", "Proxmox-2": "52894", "dns-02": "52897",
    "edge-01": "52899", "komodo-01": "52902",
    "mail-relay-01": "52904", "zabbix-01": "52908",
}
PATCH_IDS = {
    "PROXMOX": "52891", "Proxmox-2": "52893", "cloud-01": "52895",
    "dns-02": "52896", "edge-01": "52898", "greenbone-01": "52900",
    "komodo-01": "52901", "mail-relay-01": "52903",
    "monitor-01": "52905", "sensor-01": "52906", "zabbix-01": "52907",
}
PROTECTED = {"admin-01", "media-01", "dns-01", "router-01"}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def items_by_key(z, token, hostid, name):
    found = z.zabbix_api(token, "item.get", {
        "hostids": hostid,
        "filter": {"key_": ["homelab.patch.snapshot", "homelab.cpu.temperature"]},
        "output": ["itemid", "key_", "name", "type", "value_type",
                   "status", "state", "lastclock", "lastvalue"],
        "limit": 20,
    })
    result = {}
    for item in found:
        key = item["key_"]
        require(key not in result, "Duplicate telemetry item on " + name)
        result[key] = item
    return result


def verify_recent(name, items):
    patch = items.get("homelab.patch.snapshot")
    require(patch is not None and str(patch["itemid"]) == PATCH_IDS[name],
            "Patch item ID missing or changed on " + name)
    require(all(str(patch.get(k)) == v for k, v in
                (("type", "7"), ("value_type", "4"), ("status", "0"),
                 ("state", "0"), ("name", "Homelab patch snapshot (cached APT JSON)"))),
            "Patch item misconfigured on " + name)
    try:
        age = time.time() - int(patch.get("lastclock") or 0)
        value = json.loads(patch.get("lastvalue") or "")
        valid = (
            0 <= age <= 3 * 3600
            and value.get("schema_version") == 1
            and value.get("source") == "cached_apt_no_refresh"
            and value.get("error") is None
            and type(value.get("pending_updates_cached")) is int
            and value["pending_updates_cached"] >= 0
            and value.get("security_updates") is None
            and value.get("last_verified_patch_utc") is None
        )
    except (TypeError, ValueError, AttributeError, KeyError):
        valid = False
    require(valid, "No recent valid cached APT snapshot on " + name)
    temperature = items.get("homelab.cpu.temperature")
    if name not in TEMPERATURE:
        require(temperature is None, "Unexpected CPU item on sensorless host " + name)
        return None
    require(temperature is not None and str(temperature["itemid"]) == TEMPERATURE[name],
            "CPU item ID missing or changed on " + name)
    require(all(str(temperature.get(k)) == v for k, v in
                (("name", "CPU temperature"), ("type", "7"), ("value_type", "0"),
                 ("status", "0"), ("state", "0"))),
            "CPU item misconfigured on " + name)
    try:
        temp_age = time.time() - int(temperature.get("lastclock") or 0)
        t = float(temperature.get("lastvalue"))
        valid = 0 <= temp_age <= 30 * 60 and math.isfinite(t) and 1 <= t <= 110
    except (TypeError, ValueError):
        valid = False
    require(valid, "No recent valid CPU temperature history on " + name)
    return temperature


def prepare(z, name, dashboard, patch_template, cpu_item):
    panels = dashboard.get("panels")
    require(isinstance(panels, list), "Missing dashboard panels: " + name)
    by_id = {p["id"]: p for p in panels}
    require(len(by_id) == len(panels), "Duplicate panel ID on " + name)
    require({1, 90, 91, 98, 99, 100, 101, 102, 103} <= set(by_id),
            "Unexpected dashboard panel inventory: " + name)
    for row_id, title in ((100, "Host Overview"), (101, "System Performance"),
                          (102, "Host Security"), (103, "Monitoring & Alerts")):
        require(by_id[row_id].get("type") == "row"
                and by_id[row_id].get("title") == title
                and by_id[row_id].get("collapsed") is False,
                "Unexpected section row " + str(row_id) + " on " + name)
    for pid, kind in ((98, "stat"), (99, "table")):
        p = by_id[pid]
        require(p.get("type") == kind
                and p.get("datasource", {}).get("type") == "prometheus"
                and any('hostname="' + name + '"' in t.get("expr", "")
                        for t in p.get("targets", [])),
                "Greenbone panel was not host-scoped on " + name)
    old_patch = by_id[91]
    old_security_y = by_id[102]["gridPos"]["y"]
    require(by_id[101]["gridPos"]["y"] == 5, "Unexpected performance row on " + name)
    already = old_patch.get("type") == "stat" and 96 in by_id
    require((old_patch.get("type") == "text"
             and old_patch.get("title") == "Patching status")
            or (old_patch.get("type") == "stat"
                and old_patch.get("title") == "Pending patches — " + name),
            "Unexpected patch panel on " + name)
    require((96 in by_id) == (name in TEMPERATURE and already),
            "Unexpected temperature chart inventory on " + name)

    new = copy.deepcopy(dashboard)
    new_by_id = {p["id"]: p for p in new["panels"]}
    patch = copy.deepcopy(patch_template)
    require(patch.get("type") == "stat"
            and patch.get("datasource") == z.DS
            and patch.get("targets", [{}])[0].get("queryType") == "2",
            "Invalid verified patch template")
    patch["title"] = "Pending patches — " + name
    patch["targets"][0]["host"]["filter"] = name
    patch["gridPos"]["y"] = old_patch["gridPos"]["y"]
    new["panels"][panels.index(old_patch)] = patch
    new_by_id[91] = patch

    if cpu_item is not None and not already:
        performance = [
            p for p in panels
            if p.get("type") != "row"
            and p["id"] not in {1, 90, 91, 94, 95, 96, 97, 98, 99}
            and p.get("title") != "System uptime"
        ]
        require(all(p.get("type") == "timeseries"
                    and 6 <= p.get("gridPos", {}).get("y", -1) < old_security_y
                    for p in performance),
                "Unexpected performance charts on " + name)
        count = len(performance)
        expected_security_y = 6 + 8 * ((count + 1) // 2)
        require(old_security_y == expected_security_y,
                "Unexpected security row position on " + name)
        y = 6 + 8 * (count // 2)
        temp = z.metric_panel(96, "CPU temperature", name, cpu_item, y, "celsius")
        temp["gridPos"]["x"] = 12 * (count % 2)
        temp["targets"][0]["queryType"] = "3"
        temp["targets"][0]["itemids"] = TEMPERATURE[name]
        temp["targets"][0]["options"]["useTrends"] = "false"
        new["panels"].append(temp)
        new_by_id[96] = temp
        shift = 8 if count % 2 == 0 else 0
        if shift:
            for pid in (90, 91, 98, 99, 102, 103):
                new_by_id[pid]["gridPos"]["y"] += 8

    before = {p["id"]: p for p in panels}
    after = {p["id"]: p for p in new["panels"]}
    require(set(after) == set(before) | ({96} if cpu_item is not None else set()),
            "Unexpected candidate panel inventory on " + name)
    for pid in before:
        if pid == 91:
            continue
        a = copy.deepcopy(before[pid])
        b = copy.deepcopy(after[pid])
        if pid in (90, 98, 99, 102, 103):
            a["gridPos"].pop("y", None)
            b["gridPos"].pop("y", None)
        require(a == b, "Unrelated panel drift " + name + ":" + str(pid))
    for pid in (98, 99):
        require(after[pid]["datasource"] == before[pid]["datasource"]
                and after[pid]["targets"] == before[pid]["targets"],
                "Greenbone target drift on " + name)
    require(after[91]["targets"][0]["host"]["filter"] == name,
            "Patch target host mismatch on " + name)
    if cpu_item is not None:
        t = after[96]["targets"][0]
        require(after[96]["datasource"] == z.DS
                and t.get("queryType") == "3"
                and t.get("itemids") == TEMPERATURE[name]
                and t.get("host", {}).get("filter") == name,
                "Temperature target mismatch on " + name)
    if already:
        require(before == after, "Previously applied dashboard drift on " + name)
    return new


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    loader = SourceFileLoader("homelab_zabbix_rebuild", str(BUILDER))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    z = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z)
    names, token, graf_headers = z.read_secret_files()
    require(len(names) == 15
            and set(names) == set(TARGETS) | PROTECTED,
            "15-host managed inventory mismatch")

    dns_uid = "zbx-host-" + hashlib.sha256(b"dns-01").hexdigest()[:20]
    dns = z.grafana_api(graf_headers, "/api/dashboards/uid/" + dns_uid)
    dns_panels = {p["id"]: p for p in dns["dashboard"]["panels"]}
    require(dns_panels[91]["type"] == "stat"
            and dns_panels[91]["title"] == "Pending patches — dns-01",
            "Verified dns-01 patch template unavailable")

    zhosts = z.zabbix_api(token, "host.get", {
        "output": ["hostid", "host", "status"],
        "filter": {"status": "0"}, "limit": 1000,
    })
    proposals = []
    for name in TARGETS:
        matches = [h for h in zhosts if h["host"] == name]
        require(len(matches) == 1, "Enabled Zabbix host mismatch: " + name)
        items = items_by_key(z, token, matches[0]["hostid"], name)
        temp = verify_recent(name, items)
        uid = "zbx-host-" + hashlib.sha256(name.encode()).hexdigest()[:20]
        prior = z.grafana_api(graf_headers, "/api/dashboards/uid/" + uid)
        old = prior["dashboard"]
        require(old.get("uid") == uid and old.get("title") == name
                and z.MARKER in old.get("tags", [])
                and prior.get("meta", {}).get("folderUid") == "homelab-managed-devices",
                "Dashboard ownership or identity mismatch: " + name)
        candidate = prepare(z, name, old, dns_panels[91], temp)
        change = candidate["panels"] != old["panels"]
        print(("PLAN UPDATE: " if change else "PLAN EXISTS: ") + name
              + " patch=" + PATCH_IDS[name]
              + " temperature=" + TEMPERATURE.get(name, "unavailable"))
        if change:
            proposals.append((name, candidate))
    print("ESTATE TELEMETRY GUARD: 11 dashboards only; four protected; Greenbone untouched")
    print("PLAN SUMMARY: " + str(len(proposals)) + " dashboard updates")
    if not args.apply:
        print("AUDIT ONLY: no Grafana API writes")
        return
    for name, candidate in proposals:
        z.grafana_api(graf_headers, "/api/dashboards/db", "POST", {
            "dashboard": candidate, "folderUid": "homelab-managed-devices",
            "overwrite": True, "message": "Add verified cached APT and CPU telemetry",
        })
        print("APPLIED UPDATE: " + name)
    print("APPLY SUMMARY: " + str(len(proposals)) + " dashboard updates")


if __name__ == "__main__":
    main()
