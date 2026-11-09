#!/usr/bin/env python3
"""Read-only audit of router-01 local Zabbix items conflicting with Linux template.

Never prints item values, API tokens, or configuration secrets.
Does not change templates, items, host configuration, or router services.
"""
import importlib.util
import sys
from datetime import datetime, timezone
from importlib.machinery import SourceFileLoader

BUILDER = "/usr/local/sbin/homelab-grafana-zabbix-rebuild"
ROUTER = "router-01"
KEYS = (
    "system.cpu.load[all,avg1]",
    "system.uptime",
    "vm.memory.size[available]",
    "vm.memory.size[pavailable]",
    "vm.memory.size[total]",
)
STAGE = "initialization"


def main():
    global STAGE
    STAGE = "load existing Zabbix API client"
    loader = SourceFileLoader("homelab_router_local_audit_builder", BUILDER)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    z = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z)

    STAGE = "verify protected host inventory"
    names, token, _ = z.read_secret_files()
    if len(names) != 15 or ROUTER not in names:
        raise RuntimeError("Managed host inventory mismatch")

    STAGE = "retrieve router host"
    hosts = z.zabbix_api(token, "host.get", {
        "filter": {"host": [ROUTER]},
        "output": ["hostid", "host", "status"],
    })
    if len(hosts) != 1 or str(hosts[0]["status"]) != "0":
        raise RuntimeError("Router host missing, duplicated or disabled")

    STAGE = "retrieve conflicting items and trigger dependencies"
    items = z.zabbix_api(token, "item.get", {
        "hostids": [hosts[0]["hostid"]],
        "output": ["itemid", "key_", "name", "type", "status", "state",
                   "templateid", "history", "trends", "lastclock", "value_type"],
        "selectTriggers": ["triggerid"],
        "limit": 10000,
    })
    STAGE = "validate exact five local item keys"
    matched = [item for item in items if item.get("key_") in KEYS]
    if len(matched) != 5 or {item["key_"] for item in matched} != set(KEYS):
        raise RuntimeError("Expected exactly five matching existing items")
    if any(str(item.get("templateid", "0")) not in ("0", "") for item in matched):
        raise RuntimeError("At least one matching item is not locally defined")

    print("AUDIT ONLY: router-01, 5 directly defined Zabbix items")
    print("No item values or credentials are displayed")
    for item in sorted(matched, key=lambda x: x["key_"]):
        t = int(item.get("lastclock") or 0)
        last = (datetime.fromtimestamp(t, timezone.utc).isoformat()
                if t else "never")
        print("ITEM key=" + item["key_"]
              + " itemid=" + str(item["itemid"])
              + " type=" + str(item["type"])
              + " status=" + str(item["status"])
              + " state=" + str(item["state"])
              + " value_type=" + str(item["value_type"])
              + " last_data_utc=" + last
              + " history=" + str(item["history"])
              + " trends=" + str(item["trends"])
              + " direct_trigger_refs=" + str(len(item.get("triggers") or [])))
    print("NOTE: Grafana and external references may exist beyond direct Zabbix triggers")
    print("NO CHANGES MADE. Review history/dependencies before item retirement or migration")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("SAFE FAILURE: stage=" + STAGE + "; error_class=" + type(exc).__name__)
        sys.exit(1)
