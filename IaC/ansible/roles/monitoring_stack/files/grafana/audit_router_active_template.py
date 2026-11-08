#!/usr/bin/env python3
"""Read-only preflight to replace router OS Facts with Linux active template.
This never writes to Zabbix. No credentials or item values are printed.
"""
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

loader = SourceFileLoader("dashboard_builder", "/usr/local/sbin/homelab-grafana-zabbix-rebuild")
spec = importlib.util.spec_from_loader(loader.name, loader)
z = importlib.util.module_from_spec(spec)
spec.loader.exec_module(z)
_, token, _ = z.read_secret_files()

hosts = z.zabbix_api(token, "host.get", {
    "filter": {"host": ["router-01"]},
    "output": ["hostid", "host", "name", "status"],
    "selectParentTemplates": ["templateid", "name", "host"],
})
if len(hosts) != 1:
    raise RuntimeError("Expected exactly one router-01 Zabbix host")
host = hosts[0]
linked = host.get("parentTemplates") or []
print("ROUTER: router-01")
print("CURRENT TEMPLATES: " + (", ".join(t["name"] for t in linked) if linked else "NONE"))

templates = z.zabbix_api(token, "template.get", {
    "filter": {"host": ["Linux by Zabbix agent active", "Homelab Linux OS Facts"]},
    "output": ["templateid", "name", "host"],
})
lookup = {t["host"]: t for t in templates}
active = lookup.get("Linux by Zabbix agent active")
custom = lookup.get("Homelab Linux OS Facts")
if active is None or custom is None:
    raise RuntimeError("Expected active Linux and custom OS Facts templates missing")
active_items = z.zabbix_api(token, "item.get", {
    "templateids": [active["templateid"]],
    "output": ["key_", "name"], "limit": 10000,
})
custom_items = z.zabbix_api(token, "item.get", {
    "templateids": [custom["templateid"]],
    "output": ["key_", "name"], "limit": 10000,
})
active_keys = {x["key_"] for x in active_items}
custom_keys = {x["key_"] for x in custom_items}
print("LINUX ACTIVE ITEM COUNT: " + str(len(active_items)))
print("OS FACTS ITEM COUNT: " + str(len(custom_items)))
overlap = sorted(active_keys & custom_keys)
print("DUPLICATE ITEM KEYS BETWEEN TEMPLATES: " +
      (", ".join(overlap[:25]) if overlap else "NONE"))
if len(overlap) > 25:
    print("ADDITIONAL DUPLICATE KEYS: " + str(len(overlap) - 25))
host_items = z.zabbix_api(token, "item.get", {
    "hostids": [host["hostid"]],
    "output": ["itemid", "key_", "templateid", "name"], "limit": 10000,
})
custom_ids = {x["itemid"] for x in custom_items}
# Host item templateid maps to a template's itemid, not the template object id.
custom_host_items = [x for x in host_items if x.get("templateid") in custom_ids]
print("ROUTER ITEMS INHERITED FROM OS FACTS: " + str(len(custom_host_items)))
other_linked = [t["name"] for t in linked if t["templateid"] != custom["templateid"]]
print("OTHER TEMPLATES ON ROUTER: " + (", ".join(other_linked) if other_linked else "NONE"))
if any(t["templateid"] == active["templateid"] for t in linked):
    print("RESULT: Linux active already linked; avoid duplicates.")
elif overlap or other_linked:
    print("RESULT: REVIEW required before safe template replacement; do not unlink and clear automatically.")
else:
    print("RESULT: No cross-template item-key overlap found; migration is feasible with further item/history checks.")
