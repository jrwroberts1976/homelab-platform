#!/usr/bin/env python3
"""Safely add Linux by Zabbix agent active to router-01 through Zabbix API.

Read-only by default; --apply changes only the Zabbix template link.
Do not unlink/clear the existing Homelab Linux OS Facts template yet.
"""
import argparse
import importlib.util
from importlib.machinery import SourceFileLoader

BUILDER = "/usr/local/sbin/homelab-grafana-zabbix-rebuild"
ROUTER = "router-01"
ACTIVE = "Linux by Zabbix agent active"
OS_FACTS = "Homelab Linux OS Facts"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    loader = SourceFileLoader("homelab_zabbix_dashboard_builder", BUILDER)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    z = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z)
    names, token, _ = z.read_secret_files()
    if ROUTER not in names or len(names) != 15:
        raise RuntimeError("Verified managed-host inventory changed; refusing link")

    hosts = z.zabbix_api(token, "host.get", {
        "filter": {"host": [ROUTER]},
        "output": ["hostid", "host", "name", "status"],
        "selectParentTemplates": ["templateid", "name", "host"],
    })
    if len(hosts) != 1 or hosts[0]["status"] != "0":
        raise RuntimeError("router-01 not uniquely enabled in Zabbix")
    host = hosts[0]

    templates = z.zabbix_api(token, "template.get", {
        "filter": {"host": [ACTIVE, OS_FACTS]},
        "output": ["templateid", "host", "name"],
    })
    lookup = {template["host"]: template for template in templates}
    if len(templates) != 2 or set(lookup) != {ACTIVE, OS_FACTS}:
        raise RuntimeError("Expected templates not uniquely found")

    linked = host.get("parentTemplates") or []
    linked_ids = {t["templateid"] for t in linked}
    active_id = lookup[ACTIVE]["templateid"]
    facts_id = lookup[OS_FACTS]["templateid"]
    if linked_ids == {facts_id, active_id}:
        print("ALREADY LINKED: Linux by Zabbix agent active; OS Facts retained")
        return
    if linked_ids != {facts_id}:
        raise RuntimeError("Unexpected router template assignments; refusing mutation")

    # Check cross-template key collisions immediately before linking.
    keys = {}
    for template_name in (ACTIVE, OS_FACTS):
        data = z.zabbix_api(token, "item.get", {
            "templateids": [lookup[template_name]["templateid"]],
            "output": ["key_"], "limit": 10000,
        })
        keys[template_name] = {item["key_"] for item in data}
    collisions = keys[ACTIVE] & keys[OS_FACTS]
    if collisions:
        raise RuntimeError("Overlapping template item keys; no changes made")

    # Catch locally defined host items that could conflict with new template.
    host_items = z.zabbix_api(token, "item.get", {
        "hostids": [host["hostid"]],
        "output": ["key_", "templateid"], "limit": 10000,
    })
    local_collisions = {item["key_"] for item in host_items
                        if item.get("templateid") in ("0", "", None)} & keys[ACTIVE]
    if local_collisions:
        raise RuntimeError("Locally-defined host items conflict with active template")

    print("PRECHECK PASS: router-01; Linux active items=" + str(len(keys[ACTIVE]))
          + "; OS Facts items=" + str(len(keys[OS_FACTS]))
          + "; no key collisions")
    if not args.apply:
        print("AUDIT ONLY: no changes")
        return

    # host.massadd links the template without replacing prior links.
    z.zabbix_api(token, "host.massadd", {
        "hosts": [{"hostid": host["hostid"]}],
        "templates": [{"templateid": active_id}],
    })
    check = z.zabbix_api(token, "host.get", {
        "hostids": [host["hostid"]],
        "output": ["hostid"],
        "selectParentTemplates": ["templateid", "host"],
    })
    if len(check) != 1 or {t["templateid"] for t in check[0]["parentTemplates"]} != {facts_id, active_id}:
        raise RuntimeError("Post-link verification failed; inspect Zabbix templates")
    print("LINK VERIFIED: Linux by Zabbix agent active is now assigned to router-01")
    print("PRESERVED: Homelab Linux OS Facts remains linked until active data is validated")
    print("No operating-system, nftables or agent changes performed")


if __name__ == "__main__":
    main()
