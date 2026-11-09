#!/usr/bin/env python3
"""Read-only Zabbix/Grafana coverage matrix for exactly 15 managed hosts.

This reports item configuration and dashboard presentation, not package compliance,
live temperature sensor availability, or per-host Greenbone scan coverage.
"""
import hashlib
import importlib.util
import json
from importlib.machinery import SourceFileLoader
from pathlib import Path

BUILDER = Path("/usr/local/sbin/homelab-grafana-zabbix-rebuild")
KEYS = ("homelab.patch.snapshot", "homelab.cpu.temperature")


def main():
    loader = SourceFileLoader("homelab_zabbix_rebuild", str(BUILDER))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    z = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z)
    names, token, graf_headers = z.read_secret_files()
    if len(names) != 15 or len(set(names)) != 15:
        raise RuntimeError("Expected exactly 15 unique managed hosts")

    hosts = z.zabbix_api(token, "host.get", {
        "output": ["hostid", "host", "name", "status"],
        "filter": {"status": "0"},
        "selectParentTemplates": ["name"],
        "limit": 1000,
    })
    result = []
    for name in sorted(names):
        candidates = [h for h in hosts if name in (h["host"], h["name"])]
        if len(candidates) != 1:
            raise RuntimeError("Missing or ambiguous enabled Zabbix host " + name)
        host = candidates[0]
        if {x["name"] for x in host.get("parentTemplates", [])} != {
                "Linux by Zabbix agent active"}:
            raise RuntimeError("Unexpected Zabbix template on " + name)
        items = z.zabbix_api(token, "item.get", {
            "hostids": host["hostid"],
            "output": ["itemid", "name", "key_", "type", "value_type",
                       "status", "state", "lastclock", "lastvalue"],
            "limit": 10000,
        })
        telemetry = {}
        for key, expected_type in ((KEYS[0], "4"), (KEYS[1], "0")):
            matching = [i for i in items if i["key_"] == key]
            if len(matching) > 1:
                raise RuntimeError("Duplicate item " + key + " on " + name)
            if not matching:
                telemetry[key] = {"state": "MISSING"}
                continue
            item = matching[0]
            valid = (str(item["type"]) == "7"
                     and str(item["value_type"]) == expected_type
                     and str(item["status"]) == "0"
                     and str(item["state"]) == "0")
            telemetry[key] = {
                "state": "PRESENT" if valid else "MISCONFIGURED_OR_UNSUPPORTED",
                "itemid": str(item["itemid"]),
                "has_history": str(item.get("lastclock", "0")) not in ("0", ""),
            }
        uid = "zbx-host-" + hashlib.sha256(name.encode()).hexdigest()[:20]
        response = z.grafana_api(
            graf_headers, "/api/dashboards/uid/" + uid, missing_ok=True)
        if response is None:
            raise RuntimeError("Missing Grafana dashboard for " + name)
        dash = response["dashboard"]
        if (dash.get("title") != name
                or z.MARKER not in dash.get("tags", [])
                or response.get("meta", {}).get("folderUid") != "homelab-managed-devices"):
            raise RuntimeError("Unexpected Grafana dashboard identity " + name)
        panels = {p["id"]: p for p in dash["panels"]}
        if len(panels) != len(dash["panels"]):
            raise RuntimeError("Duplicate Grafana panel IDs for " + name)
        temp = panels.get(96, {})
        temp_target = temp.get("targets", [{}])[0]
        patch = panels.get(91, {})
        patch_target = patch.get("targets", [{}])[0]
        temp_status = (
            "ZABBIX_MATCH" if temp.get("title") == "CPU temperature"
            and temp.get("datasource") == z.DS
            and temp_target.get("queryType") == "3"
            and temp_target.get("host", {}).get("filter") == name
            and temp_target.get("itemids") == telemetry[KEYS[1]].get("itemid")
            else "MISSING_OR_DIFFERENT"
        )
        patch_status = (
            "ZABBIX_LIVE" if patch.get("type") == "stat"
            and patch.get("datasource") == z.DS
            and patch_target.get("queryType") == "2"
            and patch_target.get("host", {}).get("filter") == name
            else "UNKNOWN_PLACEHOLDER_OR_DIFFERENT"
        )
        greenbone = all(
            pid in panels and any(
                'hostname="' + name + '"' in t.get("expr", "")
                for t in panels[pid].get("targets", []))
            for pid in (98, 99)
        )
        result.append({
            "host": name,
            "patch_item": telemetry[KEYS[0]],
            "temp_item": telemetry[KEYS[1]],
            "grafana_patch": patch_status,
            "grafana_temperature": temp_status,
            "grafana_greenbone": "HOST_SCOPED" if greenbone else "OTHER_OR_MISSING",
            "router_generic_deployment_excluded": name == "router-01",
        })

    print("READ_ONLY TELEMETRY MATRIX: 15 hosts; Zabbix and Grafana API GET only")
    for row in result:
        print("{host:14} patch_item={patch:28} patch_panel={panel:33} "
              "temp_item={temp:28} temp_panel={tpanel:23} greenbone={greenbone}".format(
                host=row["host"],
                patch=row["patch_item"]["state"],
                panel=row["grafana_patch"],
                temp=row["temp_item"]["state"],
                tpanel=row["grafana_temperature"],
                greenbone=row["grafana_greenbone"]))
    print("MATRIX_JSON=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
