#!/usr/bin/env python3
"""Reset ONLY router-01 Zabbix legacy entities and attach passive Linux template.

Read-only default. Apply requires --apply, an auditable metadata backup and
an exact plan fingerprint from a separate dry-run. No router/ASUS SSH or changes.
WARNING: Zabbix item/trigger deletion can permanently delete history/problems.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from importlib.machinery import SourceFileLoader

BUILDER = "/usr/local/sbin/homelab-grafana-zabbix-rebuild"
BACKUP_DIR = Path("/var/lib/homelab-network-hosts/zabbix-router-rebuild-backups")
HOST_ID = "10701"
HOST = "router-01"
LEGACY = "Homelab Linux OS Facts"
TARGET = "Linux by Zabbix agent"
ACTIVE = "Linux by Zabbix agent active"
STAGE = "initialization"


def fingerprint(plan):
    return hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]


def main():
    global STAGE
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--approve-fingerprint", default="")
    args = parser.parse_args()
    if args.apply and not args.approve_fingerprint:
        raise RuntimeError("Explicit --approve-fingerprint required")

    STAGE = "load Zabbix API"
    loader = SourceFileLoader("homelab_router_rebuild", BUILDER)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    hosts_inventory, token, _ = module.read_secret_files()
    if len(hosts_inventory) != 15 or HOST not in hosts_inventory:
        raise RuntimeError("Expected managed host inventory missing")

    def api(method, params):
        return module.zabbix_api(token, method, params)

    STAGE = "inspect router host and template links"
    hosts = api("host.get", {
        "filter": {"host": [HOST]},
        "output": ["hostid", "host", "name", "status"],
        "selectParentTemplates": ["templateid", "host", "name"],
        "selectInterfaces": ["interfaceid", "type", "useip", "ip", "port", "main"],
    })
    if len(hosts) != 1 or str(hosts[0]["hostid"]) != HOST_ID or str(hosts[0]["status"]) != "0":
        raise RuntimeError("Router host identity/status has changed")
    host = hosts[0]
    interfaces = host.get("interfaces") or []
    if not any(str(i.get("type")) == "1" and str(i.get("useip")) == "1"
               and i.get("ip") == "192.168.2.1" and str(i.get("port")) == "10050"
               for i in interfaces):
        raise RuntimeError("Router Zabbix agent interface not verified")
    STAGE = "inspect templates"
    templates = api("template.get", {
        "filter": {"host": [LEGACY, TARGET, ACTIVE]},
        "output": ["templateid", "host", "name"],
    })
    by_name = {t["host"]: t for t in templates}
    if any(sum(t["host"] == n for t in templates) != 1 for n in (LEGACY, TARGET)):
        raise RuntimeError("Expected templates not uniquely resolved")
    legacy_id, target_id = by_name[LEGACY]["templateid"], by_name[TARGET]["templateid"]
    active_id = by_name.get(ACTIVE, {}).get("templateid")
    linked_ids = {t["templateid"] for t in host.get("parentTemplates") or []}
    if linked_ids == {target_id}:
        print("ALREADY REBUILT: router-01 linked to Linux by Zabbix agent only")
        return
    if linked_ids != {legacy_id}:
        raise RuntimeError("Unexpected linked templates; cannot reset automatically")
    if active_id in linked_ids:
        raise RuntimeError("Active Linux template also linked; refusing mixed setup")

    STAGE = "inspect router items and triggers"
    items = api("item.get", {
        "hostids": [HOST_ID],
        "output": ["itemid", "name", "key_", "templateid", "type", "status", "value_type"],
        "limit": 10000,
    })
    local_items = [i for i in items if str(i.get("templateid", "0")) in ("0", "", "None")]
    inherited_items = [i for i in items if i not in local_items]
    triggers = api("trigger.get", {
        "hostids": [HOST_ID],
        "output": ["triggerid", "description", "expression", "templateid", "status"],
        "selectItems": ["itemid", "hostid"],
        "limit": 10000,
    })
    local_triggers = [t for t in triggers if str(t.get("templateid", "0")) in ("0", "", "None")]
    inherited_triggers = [t for t in triggers if t not in local_triggers]
    # Refuse cross-host trigger removal; avoid affecting alerts on other devices.
    external = [t for t in local_triggers if any(str(i.get("hostid")) != HOST_ID
                for i in t.get("items") or [])]
    if external:
        raise RuntimeError("Cross-host trigger present; refuse removal")
    # Refuse unidentified inherited items/triggers not from the one permitted template.
    legacy_template_items = api("item.get", {
        "templateids": [legacy_id], "output": ["itemid"], "limit": 10000,
    })
    legacy_item_ids = {x["itemid"] for x in legacy_template_items}
    if any(str(i.get("templateid")) not in legacy_item_ids for i in inherited_items):
        raise RuntimeError("Unexpected inherited item found")
    legacy_template_triggers = api("trigger.get", {
        "templateids": [legacy_id], "output": ["triggerid"], "limit": 10000,
    })
    legacy_trigger_ids = {x["triggerid"] for x in legacy_template_triggers}
    if any(str(t.get("templateid")) not in legacy_trigger_ids for t in inherited_triggers):
        raise RuntimeError("Unexpected inherited trigger found")

    # Triggers may be tied to item prototypes or discovery. Refuse surprises.
    discovery = api("discoveryrule.get", {
        "hostids": [HOST_ID], "output": ["itemid", "name", "templateid"],
        "limit": 10000,
    })
    if discovery:
        raise RuntimeError("Discovery rules found; review before cleanup")
    graphs = api("graph.get", {
        "hostids": [HOST_ID], "output": ["graphid", "name", "templateid"],
        "limit": 10000,
    })
    if any(str(x.get("templateid")) in ("0", "", "None") for x in graphs):
        raise RuntimeError("Local graphs found; review before cleanup")
    # Validate local triggers only reference this router.
    snapshot = {
        "host": host,
        "templates": templates,
        "items": items,
        "triggers": triggers,
        "discovery_rules": discovery,
        "graphs": graphs,
    }
    plan = {
        "hostid": HOST_ID,
        "legacy_templateid": legacy_id,
        "new_templateid": target_id,
        "local_item_ids": sorted(x["itemid"] for x in local_items),
        "local_trigger_ids": sorted(x["triggerid"] for x in local_triggers),
        "legacy_inherited_item_ids": sorted(x["itemid"] for x in inherited_items),
        "legacy_inherited_trigger_ids": sorted(x["triggerid"] for x in inherited_triggers),
    }
    digest = fingerprint(plan)
    print("SCOPE: Zabbix host router-01 (10701) ONLY")
    print("PLAN: clear old Homelab Linux OS Facts link, delete old local items/alerts, link passive Linux template")
    print("COUNTS: local_items=" + str(len(local_items)) +
          " local_triggers=" + str(len(local_triggers)) +
          " legacy_inherited_items=" + str(len(inherited_items)) +
          " legacy_inherited_triggers=" + str(len(inherited_triggers)))
    print("PLAN FINGERPRINT: " + digest)
    print("WARNING: removed items/triggers lose their Zabbix history and problems")
    if not args.apply:
        print("AUDIT ONLY: no changes")
        return
    if args.approve_fingerprint != digest:
        raise RuntimeError("Plan changed since audit; refusing to delete")

    STAGE = "write metadata backup"
    BACKUP_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    if BACKUP_DIR.is_symlink() or (BACKUP_DIR.stat().st_mode & 0o077):
        raise RuntimeError("Backup directory permissions unsafe")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fd, tmp = tempfile.mkstemp(prefix=".router-01-", suffix=".json", dir=BACKUP_DIR)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump({"timestamp_utc": stamp, "fingerprint": digest, "snapshot": snapshot},
                      out, indent=2)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.chmod(tmp, 0o600)
        backup_path = BACKUP_DIR / ("router-01-" + stamp + "-" + digest + ".json")
        os.replace(tmp, backup_path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    print("BACKUP SAVED: " + str(backup_path))
    # Metadata backup cannot restore history once Zabbix removes it.
    STAGE = "delete old local router triggers"
    if local_triggers:
        api("trigger.delete", [x["triggerid"] for x in local_triggers])
    STAGE = "delete old local router items"
    if local_items:
        api("item.delete", [x["itemid"] for x in local_items])
    STAGE = "unlink and clear legacy OS Facts template on router only"
    api("host.update", {"hostid": HOST_ID, "templates_clear": [{"templateid": legacy_id}]})
    STAGE = "link passive Linux template"
    api("host.massadd", {
        "hosts": [{"hostid": HOST_ID}],
        "templates": [{"templateid": target_id}],
    })
    STAGE = "verify final router template links"
    verify = api("host.get", {
        "hostids": [HOST_ID], "output": ["hostid"],
        "selectParentTemplates": ["templateid", "host"],
    })
    if len(verify) != 1 or {x["templateid"] for x in verify[0]["parentTemplates"]} != {target_id}:
        raise RuntimeError("Final linked template verification failed")
    print("SUCCESS: router-01 now linked only to Linux by Zabbix agent")
    print("No router, ASUS access-point, nftables or PPPoE changes performed")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("SAFE FAILURE: stage=" + STAGE + "; error_class=" + type(exc).__name__)
        sys.exit(1)
