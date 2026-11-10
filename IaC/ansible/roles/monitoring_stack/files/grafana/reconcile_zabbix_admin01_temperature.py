#!/usr/bin/env python3
"""Audit or create only admin-01's read-only CPU temperature item in Zabbix."""
import argparse
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

HOST = "admin-01"
KEY = "homelab.cpu.temperature"
BUILDER = Path("/usr/local/sbin/homelab-grafana-zabbix-rebuild")


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
    if HOST not in names:
        raise RuntimeError("admin-01 missing from managed host inventory")
    hosts = z.zabbix_api(token, "host.get", {
        "output": ["hostid", "host", "status"],
        "filter": {"host": [HOST]},
        "selectParentTemplates": ["name"],
    })
    if len(hosts) != 1 or hosts[0]["host"] != HOST or str(hosts[0]["status"]) != "0":
        raise RuntimeError("Expected one enabled admin-01 host")
    host = hosts[0]
    linked = {x["name"] for x in host.get("parentTemplates", [])}
    if linked != {"Linux by Zabbix agent active"}:
        raise RuntimeError("Unexpected linked templates: " + str(sorted(linked)))
    items = z.zabbix_api(token, "item.get", {
        "hostids": host["hostid"],
        "output": ["itemid", "key_", "type", "value_type", "status", "delay", "units"],
        "filter": {"key_": KEY},
        "limit": 100,
    })
    print("HOST: " + HOST + " | ITEM: " + KEY)
    if items:
        if len(items) != 1:
            raise RuntimeError("Duplicate temperature items")
        existing = items[0]
        if (str(existing["type"]) != "7"
                or str(existing["value_type"]) != "0"
                or str(existing["status"]) != "0"
                or existing.get("units") != "°C"):
            raise RuntimeError("Existing item config differs; refusing overwrite")
        print("EXISTS: " + KEY + " (no changes)")
        return
    print("PLAN: create one active Zabbix float item, 1m interval, units °C")
    if not args.apply:
        print("AUDIT ONLY: no Zabbix write")
        return
    created = z.zabbix_api(token, "item.create", {
        "hostid": host["hostid"], "name": "CPU temperature",
        "key_": KEY, "type": 7, "value_type": 0,
        "delay": "1m", "units": "°C", "history": "7d",
        "trends": "365d", "status": 0,
        "description": "Raspberry Pi thermal_zone0 via Agent 2, Celsius.",
    })
    verify = z.zabbix_api(token, "item.get", {
        "hostids": host["hostid"],
        "output": ["itemid", "key_", "type", "value_type", "status", "units"],
        "filter": {"key_": KEY},
    })
    if (len(verify) != 1 or str(verify[0]["type"]) != "7"
            or str(verify[0]["value_type"]) != "0"
            or str(verify[0]["status"]) != "0"
            or verify[0].get("units") != "°C"
            or str(verify[0]["itemid"]) not in
            {str(x) for x in created.get("itemids", [])}):
        raise RuntimeError("Zabbix item create verification failed")
    print("CREATED AND VERIFIED: " + KEY)
    print("Wait for first 1m collection and check Latest data")


if __name__ == "__main__":
    main()
