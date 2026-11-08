#!/usr/bin/env python3
"""Guarded Zabbix API link of passive Linux template on router-01.

Default is read-only; --apply links template ONLY, never changes router
services, nftables, agent configuration, host interfaces or existing templates.
"""
import argparse
import importlib.util
import re
import sys
from importlib.machinery import SourceFileLoader

BUILDER = "/usr/local/sbin/homelab-grafana-zabbix-rebuild"
ROUTER = "router-01"
PASSIVE = "Linux by Zabbix agent"
ACTIVE = "Linux by Zabbix agent active"
OS_FACTS = "Homelab Linux OS Facts"
STEP = "initialization"


def main():
    global STEP
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    STEP = "load existing Zabbix client"
    loader = SourceFileLoader("homelab_zabbix_builder_passive", BUILDER)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    z = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z)

    STEP = "load confirmed inventory"
    names, token, _ = z.read_secret_files()
    if len(names) != 15 or ROUTER not in names:
        raise RuntimeError("Confirmed inventory changed")

    STEP = "retrieve router host"
    hosts = z.zabbix_api(token, "host.get", {
        "filter": {"host": [ROUTER]},
        "output": ["hostid", "host", "name", "status"],
        "selectParentTemplates": ["templateid", "host", "name"],
        "selectInterfaces": ["type", "ip", "port", "useip", "main"],
    })
    if len(hosts) != 1 or str(hosts[0]["status"]) != "0":
        raise RuntimeError("Router host not uniquely enabled")
    host = hosts[0]

    STEP = "retrieve Linux templates"
    templates = z.zabbix_api(token, "template.get", {
        "filter": {"host": [PASSIVE, ACTIVE, OS_FACTS]},
        "output": ["templateid", "host", "name"],
    })
    matches = {}
    for t in templates:
        matches.setdefault(t["host"], []).append(t)
    if any(len(matches.get(key, [])) != 1 for key in (PASSIVE, OS_FACTS)):
        raise RuntimeError("Required template lookup not unique")
    passive_id = matches[PASSIVE][0]["templateid"]
    facts_id = matches[OS_FACTS][0]["templateid"]
    active_ids = {t["templateid"] for t in matches.get(ACTIVE, [])}

    STEP = "validate current linked templates"
    linked_ids = {t["templateid"] for t in host.get("parentTemplates") or []}
    if linked_ids & active_ids:
        raise RuntimeError("Active Linux template already linked; refuse dual template")
    if linked_ids == {passive_id, facts_id}:
        print("ALREADY LINKED: Linux by Zabbix agent; OS Facts preserved")
        return
    if linked_ids != {facts_id}:
        raise RuntimeError("Unexpected current template links")

    STEP = "verify passive router agent interface"
    interfaces = host.get("interfaces") or []
    if not any(str(i.get("type")) == "1"
               and str(i.get("port")) == "10050"
               and str(i.get("useip")) == "1"
               and i.get("ip") == "192.168.2.1"
               for i in interfaces):
        raise RuntimeError("Router agent interface does not match 192.168.2.1:10050")

    STEP = "inspect template item key collisions"
    keys = {}
    for label, template_id in ((PASSIVE, passive_id), (OS_FACTS, facts_id)):
        result = z.zabbix_api(token, "item.get", {
            "templateids": [template_id],
            "output": ["key_"],
            "limit": 10000,
        })
        if not result:
            raise RuntimeError("Template has no items")
        keys[label] = {rec["key_"] for rec in result}
    if keys[PASSIVE] & keys[OS_FACTS]:
        raise RuntimeError("OS Facts and passive Linux template item keys overlap")

    STEP = "inspect existing router host items"
    existing = z.zabbix_api(token, "item.get", {
        "hostids": [host["hostid"]],
        "output": ["key_", "templateid"],
        "limit": 10000,
    })
    # Existing OS Facts inherited items remain; other host items must not
    # conflict with Linux by Zabbix agent item keys either.
    facts_items = z.zabbix_api(token, "item.get", {
        "templateids": [facts_id],
        "output": ["itemid"],
        "limit": 10000,
    })
    facts_item_ids = {rec["itemid"] for rec in facts_items}
    unexpected = {rec["key_"] for rec in existing
                  if rec["key_"] in keys[PASSIVE]
                  and rec.get("templateid") not in facts_item_ids}
    if unexpected:
        # Print Zabbix item-key metadata, not secret values.
        def safe_key(value):
            return re.sub(r"[^a-zA-Z0-9_.,/\\[\\]-]", "?", str(value))[:120]
        print("HOST ITEM COLLISIONS: " + str(len(unexpected)))
        for key in sorted(unexpected)[:20]:
            sources = sorted({
                "local" if rec.get("templateid") in ("0", "", None)
                else "inherited-from-item:" + str(rec.get("templateid"))
                for rec in existing if rec["key_"] == key
            })
            print("COLLISION: key=" + safe_key(key) + " source=" + ",".join(sources))
        print("DECISION: no changes; review existing Zabbix items")
        raise RuntimeError("Host item key collision with passive Linux template")

    print("PRECHECK PASS: router-01 passive template; " +
          str(len(keys[PASSIVE])) + " passive items; " +
          str(len(keys[OS_FACTS])) + " preserved OS Facts items; 0 known item key collisions")
    print("TARGET: Zabbix-only template link; no router/AP service or firewall changes")
    if not args.apply:
        print("AUDIT ONLY: no changes")
        return

    STEP = "link passive template"
    z.zabbix_api(token, "host.massadd", {
        "hosts": [{"hostid": host["hostid"]}],
        "templates": [{"templateid": passive_id}],
    })

    STEP = "verify passive template link"
    verify = z.zabbix_api(token, "host.get", {
        "hostids": [host["hostid"]],
        "output": ["hostid"],
        "selectParentTemplates": ["templateid"],
    })
    if len(verify) != 1 or {t["templateid"] for t in verify[0]["parentTemplates"]} != {passive_id, facts_id}:
        raise RuntimeError("Post-apply template state did not match expected")
    print("LINK VERIFIED: Linux by Zabbix agent")
    print("PRESERVED: Homelab Linux OS Facts")
    print("No router/AP configuration changes performed")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Never print exception text, traceback, tokens or API credentials.
        print("SAFE FAILURE: stage=" + STEP + "; error_class=" + type(exc).__name__)
        sys.exit(1)
