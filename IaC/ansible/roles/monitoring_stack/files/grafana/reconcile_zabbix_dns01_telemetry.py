#!/usr/bin/env python3
"""Preview/create only dns-01's two pilot Zabbix active-agent items."""
import argparse
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

HOST = "dns-01"
BUILDER = Path("/usr/local/sbin/homelab-grafana-zabbix-rebuild")
SPECS = (
    {"name": "Homelab patch snapshot (cached APT JSON)",
     "key_": "homelab.patch.snapshot", "type": 7, "value_type": 4,
     "delay": "1h", "history": "7d", "status": 0},
    {"name": "CPU temperature", "key_": "homelab.cpu.temperature",
     "type": 7, "value_type": 0, "delay": "1m", "history": "7d",
     "trends": "365d", "units": "°C", "status": 0},
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    loader = SourceFileLoader("homelab_zabbix_rebuild", str(BUILDER))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    z = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z)
    names, token, _ = z.read_secret_files()
    if len(names) != 15 or HOST not in names:
        raise RuntimeError("Managed host inventory mismatch")
    hosts = z.zabbix_api(token, "host.get", {
        "output": ["hostid", "host", "status"],
        "filter": {"host": [HOST]},
        "selectParentTemplates": ["name"],
    })
    if len(hosts) != 1 or hosts[0]["host"] != HOST or str(hosts[0]["status"]) != "0":
        raise RuntimeError("Expected one enabled dns-01 Zabbix host")
    host = hosts[0]
    if {x["name"] for x in host.get("parentTemplates", [])} != {"Linux by Zabbix agent active"}:
        raise RuntimeError("Unexpected dns-01 linked templates")

    # Preflight *both* keys before making either create API call.
    missing = []
    for item in SPECS:
        existing = z.zabbix_api(token, "item.get", {
            "hostids": host["hostid"], "filter": {"key_": item["key_"]},
            "output": ["itemid", "name", "key_", "type", "value_type",
                       "status", "delay", "history", "trends", "units"],
            "limit": 100,
        })
        if len(existing) > 1:
            raise RuntimeError("Duplicate Zabbix key: " + item["key_"])
        if existing:
            got = existing[0]
            for field in ("name", "key_", "type", "value_type", "status", "units"):
                expected = str(item.get(field, ""))
                if str(got.get(field, "")) != expected:
                    raise RuntimeError("Existing item mismatch for " + item["key_"] + " field " + field)
            print("EXISTS: " + item["key_"] + " itemid=" + str(got["itemid"]))
        else:
            missing.append(item)
            print("PLAN CREATE: " + item["key_"])
    if not args.apply:
        print("AUDIT ONLY: no Zabbix API writes")
        return

    for item in missing:
        payload = dict(item, hostid=host["hostid"])
        created = z.zabbix_api(token, "item.create", payload)
        verify = z.zabbix_api(token, "item.get", {
            "hostids": host["hostid"], "filter": {"key_": item["key_"]},
            "output": ["itemid", "key_", "type", "value_type", "status", "units"],
        })
        if (len(verify) != 1 or
            str(verify[0]["itemid"]) not in
                {str(x) for x in created.get("itemids", [])} or
            str(verify[0]["type"]) != "7" or
            str(verify[0]["value_type"]) != str(item["value_type"]) or
            str(verify[0]["status"]) != "0"):
            raise RuntimeError("Create verification failed for " + item["key_"])
        print("CREATED AND VERIFIED: " + item["key_"] +
              " itemid=" + str(verify[0]["itemid"]))
    print("Item presence verified; wait for Zabbix Latest data before Grafana change")


if __name__ == "__main__":
    main()
