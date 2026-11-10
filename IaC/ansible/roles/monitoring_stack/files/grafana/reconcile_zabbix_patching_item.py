#!/usr/bin/env python3
"""Audit/create exactly one active JSON patch snapshot item on admin-01."""
import argparse
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

BUILDER = Path("/usr/local/sbin/homelab-grafana-zabbix-rebuild")
KEY = "homelab.patch.snapshot"
HOST = "admin-01"

def api_client():
    loader = SourceFileLoader("homelab_zabbix_rebuild", str(BUILDER))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    z = api_client()
    names, token, _ = z.read_secret_files()
    if HOST not in names or len(names) != 15:
        raise RuntimeError("Managed host inventory mismatch")
    hosts = z.zabbix_api(token, "host.get", {
        "output": ["hostid", "host", "status"],
        "filter": {"host": HOST},
        "selectParentTemplates": ["name"],
    })
    if len(hosts) != 1 or hosts[0]["host"] != HOST or str(hosts[0]["status"]) != "0":
        raise RuntimeError("Expected one enabled admin-01 Zabbix host")
    host = hosts[0]
    linked = {t["name"] for t in host.get("parentTemplates", [])}
    if linked != {"Linux by Zabbix agent active"}:
        raise RuntimeError("Unexpected admin-01 template assignments: " + str(sorted(linked)))
    items = z.zabbix_api(token, "item.get", {
        "hostids": host["hostid"],
        "output": ["itemid", "hostid", "key_", "type", "value_type", "status", "delay", "name"],
        "filter": {"key_": KEY},
        "limit": 100,
    })
    print("HOST: admin-01 | ITEM KEY: " + KEY)
    if items:
        if len(items) != 1:
            raise RuntimeError("Duplicate matching items; refusing changes")
        item = items[0]
        print("EXISTING ITEM: " + str(item))
        if str(item["type"]) != "7" or str(item["value_type"]) != "4":
            raise RuntimeError("Existing item is not active-agent text; manual review")
        print("No changes made; existing matching item preserved")
        return
    print("PLAN: create one enabled Zabbix agent (active) TEXT item, delay=1h, history=7d")
    if not args.apply:
        print("AUDIT ONLY: no Zabbix API changes")
        return
    created = z.zabbix_api(token, "item.create", {
        "hostid": host["hostid"],
        "name": "Homelab patch snapshot (cached APT JSON)",
        "key_": KEY,
        "type": 7,
        "value_type": 4,
        "delay": "1h",
        "history": "7d",
        "status": 0,
        "description": "Read-only cached APT snapshot. Security update count and verified patch time null until proven. No APT refresh.",
    })
    verify = z.zabbix_api(token, "item.get", {
        "hostids": host["hostid"],
        "output": ["itemid", "key_", "type", "value_type", "status"],
        "filter": {"key_": KEY},
    })
    if len(verify) != 1 or str(verify[0]["type"]) != "7" or str(verify[0]["value_type"]) != "4":
        raise RuntimeError("Post-create item verification failed")
    if str(verify[0]["itemid"]) not in {str(x) for x in created.get("itemids", [])}:
        raise RuntimeError("Created item ID verification failed")
    print("CREATED AND VERIFIED: " + KEY + " itemid=" + str(verify[0]["itemid"]))
    print("Data arrival not yet verified; check Latest data after active check configuration refresh")

if __name__ == "__main__":
    main()
