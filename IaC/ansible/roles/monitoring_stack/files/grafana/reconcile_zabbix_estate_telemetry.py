#!/usr/bin/env python3
"""Preview or reconcile only the verified 11-host Zabbix Agent 2 telemetry rollout.

No templates, existing items, router or Grafana dashboards are modified.
Run with --apply only after reviewing the preview.
"""
import argparse
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

BUILDER = Path("/usr/local/sbin/homelab-grafana-zabbix-rebuild")
TARGETS = (
    "PROXMOX", "Proxmox-2", "cloud-01", "dns-02", "edge-01",
    "greenbone-01", "komodo-01", "mail-relay-01",
    "monitor-01", "sensor-01", "zabbix-01",
)
TEMPERATURE_HOSTS = frozenset((
    "PROXMOX", "Proxmox-2", "dns-02", "edge-01",
    "komodo-01", "mail-relay-01", "zabbix-01",
))
PILOTS = frozenset(("admin-01", "media-01", "dns-01"))
PATCH = {
    "name": "Homelab patch snapshot (cached APT JSON)",
    "key_": "homelab.patch.snapshot", "type": 7, "value_type": 4,
    "delay": "1h", "history": "7d", "status": 0,
}
TEMP = {
    "name": "CPU temperature", "key_": "homelab.cpu.temperature",
    "type": 7, "value_type": 0, "delay": "1m", "history": "7d",
    "trends": "365d", "units": "°C", "status": 0,
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()

    loader = SourceFileLoader("homelab_zabbix_rebuild", str(BUILDER))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    z = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z)
    names, token, _ = z.read_secret_files()
    if set(names) != set(TARGETS) | PILOTS | {"router-01"} or len(names) != 15:
        raise RuntimeError("Zabbix managed host inventory does not match 15-host plan")
    hosts = z.zabbix_api(token, "host.get", {
        "output": ["hostid", "host", "name", "status"],
        "filter": {"status": "0"},
        "selectParentTemplates": ["name"], "limit": 1000,
    })
    targets = {}
    for name in TARGETS:
        matched = [h for h in hosts if h["host"] == name]
        if len(matched) != 1:
            raise RuntimeError("Expected exactly one enabled Zabbix host " + name)
        host = matched[0]
        if {t["name"] for t in host.get("parentTemplates", [])} != {
                "Linux by Zabbix agent active"}:
            raise RuntimeError("Unexpected Zabbix templates on " + name)
        targets[name] = host
    planned = []
    for name, host in targets.items():
        specs = (PATCH, TEMP) if name in TEMPERATURE_HOSTS else (PATCH,)
        for template in specs:
            item = dict(template)
            key = item["key_"]
            existing = z.zabbix_api(token, "item.get", {
                "hostids": host["hostid"],
                "filter": {"key_": key},
                "output": ["itemid", "name", "key_", "type",
                           "value_type", "status", "units"],
                "limit": 100,
            })
            if len(existing) > 1:
                raise RuntimeError("Duplicate item key on " + name + ": " + key)
            if existing:
                got = existing[0]
                for field in ("name", "key_", "type", "value_type",
                              "status", "units"):
                    if str(got.get(field, "")) != str(item.get(field, "")):
                        raise RuntimeError("Existing item mismatch on " + name
                                           + " " + key + " field=" + field)
                print("EXISTS: " + name + " " + key + " itemid=" + str(got["itemid"]))
            else:
                planned.append((name, host["hostid"], item))
                print("PLAN CREATE: " + name + " " + key)

    if len(planned) > 18:
        raise RuntimeError("More than 18 items in plan")
    print("PLAN SUMMARY: " + str(len(planned))
          + " new items; 11 target hosts; router and three pilots excluded")
    if not args.apply:
        print("AUDIT ONLY: no Zabbix API writes")
        return

    for name, hostid, item in planned:
        created = z.zabbix_api(token, "item.create", dict(item, hostid=hostid))
        matches = z.zabbix_api(token, "item.get", {
            "hostids": hostid, "filter": {"key_": item["key_"]},
            "output": ["itemid", "name", "key_", "type",
                       "value_type", "status", "units"],
        })
        if len(matches) != 1:
            raise RuntimeError("Item verification failed on " + name)
        got = matches[0]
        if str(got["itemid"]) not in {str(x) for x in created.get("itemids", [])}:
            raise RuntimeError("Unexpected created itemid on " + name)
        for field in ("name", "key_", "type", "value_type", "status", "units"):
            if str(got.get(field, "")) != str(item.get(field, "")):
                raise RuntimeError("Created item drift on " + name + " field=" + field)
        print("CREATED AND VERIFIED: " + name + " " + item["key_"]
              + " itemid=" + str(got["itemid"]))
    print("Registration verified; confirm Latest data before Grafana rollout")


if __name__ == "__main__":
    main()
