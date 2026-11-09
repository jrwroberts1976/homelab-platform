#!/usr/bin/env python3
"""Read-only audit of Zabbix memory and filesystem metric keys for Grafana.

Queries only verified managed hosts; reads no item values or credentials to output.
No Zabbix/Grafana writes, host service changes or system package operations.
"""
import importlib.util
import re
from importlib.machinery import SourceFileLoader

loader = SourceFileLoader("homelab_zbx_metric_audit", "/usr/local/sbin/homelab-grafana-zabbix-rebuild")
spec = importlib.util.spec_from_loader(loader.name, loader)
z = importlib.util.module_from_spec(spec)
spec.loader.exec_module(z)
names, token, _ = z.read_secret_files()
if len(names) != 15 or "router-01" not in names:
    raise RuntimeError("Expected protected inventory of 15 managed hosts")
hosts = z.zabbix_api(token, "host.get", {
    "output": ["hostid", "host", "status"],
    "filter": {"status": "0"},
    "limit": 1000,
})
by_name = {}
for name in names:
    matched = [h for h in hosts if h["host"] == name]
    if len(matched) != 1:
        raise RuntimeError("Host mismatch for " + name)
    by_name[name] = matched[0]

pattern = re.compile(r"^(?:vm\.memory\.|vfs\.fs\.|vfs\.fs\.get|vfs\.fs\.discovery)", re.I)
for name in sorted(names):
    h = by_name[name]
    items = z.zabbix_api(token, "item.get", {
        "hostids": [h["hostid"]],
        "output": ["itemid", "name", "key_", "status", "state", "lastclock"],
        "limit": 10000,
    })
    matched = sorted([i for i in items if pattern.search(i["key_"])],
                     key=lambda i: i["key_"])
    print("HOST: " + name + " matching_metrics=" + str(len(matched)))
    for i in matched[:40]:
        # Print item keys and names only; never values, secrets or parameters.
        key = i["key_"][:150].replace("\n", " ")
        display_name = i["name"][:120].replace("\n", " ")
        print("  key=" + key + " | name=" + display_name +
              " | enabled=" + str(i["status"] == "0") +
              " supported=" + str(i["state"] == "0") +
              " collected=" + str(i["lastclock"] not in ("0", "", None)))
    if len(matched) > 40:
        print("  ... remaining=" + str(len(matched) - 40))
print("AUDIT ONLY: 15 managed hosts; no changes")
