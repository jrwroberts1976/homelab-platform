#!/usr/bin/env python3
"""Migrate only router-01 from standard passive to standard active Linux template.

Default is read-only. Apply requires a plan fingerprint and writes a metadata
snapshot. Zabbix API only: no router/AP SSH, agent restart or firewall changes.
WARNING: clearing the passive template removes its inherited item history.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from importlib.machinery import SourceFileLoader
from pathlib import Path

BUILDER = "/usr/local/sbin/homelab-grafana-zabbix-rebuild"
BACKUPS = Path("/var/lib/homelab-network-hosts/zabbix-router-rebuild-backups")
HOST, HOST_ID = "router-01", "10701"
PASSIVE, ACTIVE = "Linux by Zabbix agent", "Linux by Zabbix agent active"
STAGE = "initialization"


def digest_plan(plan):
    return hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]


def main():
    global STAGE
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--approve-fingerprint", default="")
    args = ap.parse_args()
    if args.apply and not args.approve_fingerprint:
        raise RuntimeError("Explicit fingerprint approval required")

    STAGE = "load trusted API client"
    loader = SourceFileLoader("homelab_router_active_migration", BUILDER)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    z = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z)
    names, token, _ = z.read_secret_files()
    if len(names) != 15 or HOST not in names:
        raise RuntimeError("Managed host inventory changed")
    api = lambda method, params: z.zabbix_api(token, method, params)

    STAGE = "inspect router Zabbix host"
    hosts = api("host.get", {
        "filter": {"host": [HOST]},
        "output": ["hostid", "host", "status"],
        "selectParentTemplates": ["templateid", "host", "name"],
        "selectInterfaces": ["interfaceid", "type", "main", "useip", "ip", "port"],
    })
    if len(hosts) != 1 or str(hosts[0]["hostid"]) != HOST_ID or str(hosts[0]["status"]) != "0":
        raise RuntimeError("router-01 host identity/status mismatch")
    host = hosts[0]

    STAGE = "resolve standard Linux templates"
    templates = api("template.get", {
        "filter": {"host": [PASSIVE, ACTIVE]},
        "output": ["templateid", "host"],
    })
    by_name = {name: [t for t in templates if t["host"] == name] for name in (PASSIVE, ACTIVE)}
    if any(len(matches) != 1 for matches in by_name.values()):
        raise RuntimeError("Expected unique Linux templates not found")
    passive_id = by_name[PASSIVE][0]["templateid"]
    active_id = by_name[ACTIVE][0]["templateid"]

    linked_ids = {t["templateid"] for t in host.get("parentTemplates") or []}
    if linked_ids == {active_id}:
        print("ALREADY MIGRATED: router-01 has Linux by Zabbix agent active only")
        return
    if linked_ids != {passive_id}:
        raise RuntimeError("Unexpected linked templates; refuse switch")

    STAGE = "inspect existing router Zabbix objects"
    items = api("item.get", {
        "hostids": [HOST_ID],
        "output": ["itemid", "name", "key_", "templateid", "status", "state", "type"],
        "limit": 10000,
    })
    passive_items = api("item.get", {
        "templateids": [passive_id],
        "output": ["itemid", "key_"],
        "limit": 10000,
    })
    active_items = api("item.get", {
        "templateids": [active_id],
        "output": ["itemid", "key_"],
        "limit": 10000,
    })
    passive_item_ids = {i["itemid"] for i in passive_items}
    inherited = [i for i in items if str(i.get("templateid")) in passive_item_ids]
    local_items = [i for i in items if str(i.get("templateid", "0")) in ("0", "", "None")]
    unexpected = [i for i in items if i not in inherited and i not in local_items]
    print("ITEM AUDIT: total=" + str(len(items)) +
          " inherited_from_passive=" + str(len(inherited)) +
          " unlinked_or_discovered=" + str(len(local_items)) +
          " inherited_other=" + str(len(unexpected)))
    if unexpected:
        print("UNEXPECTED ITEM DETAILS (up to 20):")
        for item in unexpected[:20]:
            print("  itemid=" + str(item["itemid"]) +
                  " parent_itemid=" + str(item.get("templateid")) +
                  " type=" + str(item.get("type")))
        raise RuntimeError("Unexpected inherited Zabbix item; manual review needed")
    new_keys = {i["key_"] for i in active_items}
    conflicting_local = sorted(i["key_"] for i in local_items if i["key_"] in new_keys)
    if conflicting_local:
        print("LOCAL KEY CONFLICTS: " + str(len(conflicting_local)))
        for key in conflicting_local[:20]:
            # Keys are Zabbix metadata. Limit displayed detail and avoid values.
            print("CONFLICTING ITEM KEY: " + key[:120])
        raise RuntimeError("Local items conflict with target active template")
    if not inherited or not active_items:
        print("TEMPLATE ITEM AUDIT: passive_inherited=" + str(len(inherited)) + " active_template=" + str(len(active_items)))
        raise RuntimeError("Expected passive and active items missing")
    triggers = api("trigger.get", {
        "hostids": [HOST_ID],
        "output": ["triggerid", "description", "templateid", "status"],
        "selectItems": ["hostid", "itemid"],
        "limit": 10000,
    })
    local_triggers = [t for t in triggers if str(t.get("templateid", "0")) in ("0", "", "None")]
    if local_triggers:
        print("LOCAL TRIGGER COUNT: " + str(len(local_triggers)))
        raise RuntimeError("Locally defined triggers present; review before switching")
    discovery = api("discoveryrule.get", {
        "hostids": [HOST_ID],
        "output": ["itemid", "key_", "templateid"], "limit": 10000,
    })
    unexpected_rules = [r for r in discovery if str(r.get("templateid")) not in passive_item_ids]
    if unexpected_rules:
        print("UNEXPECTED DISCOVERY RULE COUNT: " + str(len(unexpected_rules)))
        raise RuntimeError("Locally defined or unexpected discovery rules")
    graphs = api("graph.get", {
        "hostids": [HOST_ID],
        "output": ["graphid", "name", "templateid"], "limit": 10000,
    })
    local_graphs = [g for g in graphs if str(g.get("templateid", "0")) in ("0", "", "None")]
    if local_graphs:
        print("LOCAL GRAPH COUNT: " + str(len(local_graphs)))
        raise RuntimeError("Local graphs exist; review dependencies")
    interfaces = host.get("interfaces") or []

    plan = {
        "hostid": HOST_ID, "passive_templateid": passive_id,
        "active_templateid": active_id,
        "passive_inherited_ids": sorted(i["itemid"] for i in inherited),
        "local_ids_preserved": sorted(i["itemid"] for i in local_items),
        "inherited_trigger_ids": sorted(t["triggerid"] for t in triggers),
        "discovery_rule_ids": sorted(r["itemid"] for r in discovery),
        "interface_ids_preserved": sorted(i["interfaceid"] for i in interfaces),
    }
    fingerprint = digest_plan(plan)
    print("SCOPE: router-01 (10701), Zabbix API only")
    print("CURRENT: Linux by Zabbix agent (passive)")
    print("TARGET: Linux by Zabbix agent active")
    print("AUDIT: inherited_items=" + str(len(inherited)) +
          " local_items_preserved=" + str(len(local_items)) +
          " inherited_triggers=" + str(len(triggers)) +
          " discovery_rules=" + str(len(discovery)))
    print("PLAN FINGERPRINT: " + fingerprint)
    print("WARNING: clearing passive template permanently removes inherited item/alert history")
    if not args.apply:
        print("AUDIT ONLY: no changes")
        return
    if fingerprint != args.approve_fingerprint:
        raise RuntimeError("Approval fingerprint does not match current state")

    STAGE = "save secure Zabbix metadata snapshot"
    BACKUPS.mkdir(mode=0o700, parents=True, exist_ok=True)
    if BACKUPS.is_symlink() or BACKUPS.stat().st_mode & 0o077:
        raise RuntimeError("Unsafe backup directory")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fd, path = tempfile.mkstemp(prefix=".router-active-", suffix=".json", dir=BACKUPS)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump({"timestamp_utc": stamp, "plan": plan, "host": host,
                       "items": items, "triggers": triggers, "discovery": discovery,
                       "graphs": graphs}, file, indent=2)
            file.flush()
            os.fsync(file.fileno())
        os.chmod(path, 0o600)
        dst = BACKUPS / ("router-active-" + stamp + "-" + fingerprint + ".json")
        os.replace(path, dst)
    finally:
        if os.path.exists(path):
            os.unlink(path)
    print("BACKUP SAVED: " + str(dst))

    STAGE = "replace passive with active Linux template"
    # One host.update call, never unlink-only (which leaves conflicting local
    # items); clear passive inheritance and link active simultaneously.
    api("host.update", {
        "hostid": HOST_ID,
        "templates_clear": [{"templateid": passive_id}],
        "templates": [{"templateid": active_id}],
    })
    STAGE = "verify active template relationship"
    final = api("host.get", {
        "hostids": [HOST_ID],
        "output": ["hostid"],
        "selectParentTemplates": ["templateid", "host"],
    })
    if len(final) != 1 or {t["templateid"] for t in final[0]["parentTemplates"]} != {active_id}:
        raise RuntimeError("Template replacement verification failed")
    print("SUCCESS: router-01 linked only to Linux by Zabbix agent active")
    print("No router/AP/agent/firewall changes; verify latest data before retiring passive access")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("SAFE FAILURE: stage=" + STAGE + "; error_class=" + type(exc).__name__)
        sys.exit(1)
