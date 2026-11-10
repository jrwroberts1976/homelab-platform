#!/usr/bin/env python3
"""Intentionally discard router-01 Zabbix host 10701 and recreate active-only.

Read-only default. --apply requires fingerprint of fresh audit. NO BACKUP
per operator instruction; deletes all old Zabbix host history, alerts and items.
Only Zabbix API host record changes; no router or ASUS configuration changes.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from importlib.machinery import SourceFileLoader

BUILDER = "/usr/local/sbin/homelab-grafana-zabbix-rebuild"
NAME, OLD_ID = "router-01", "10701"
GROUP = "Homelab/Linux"
ACTIVE = "Linux by Zabbix agent active"
PASSIVE = "Linux by Zabbix agent"
STAGE = "initialization"


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]


def main():
    global STAGE
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--approve-fingerprint", default="")
    args = parser.parse_args()
    if args.apply and not args.approve_fingerprint:
        raise RuntimeError("Approval fingerprint required")

    STAGE = "load Zabbix API"
    loader = SourceFileLoader("router_zabbix_recreate", BUILDER)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    z = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z)
    names, token, _ = z.read_secret_files()
    if len(names) != 15 or NAME not in names:
        raise RuntimeError("Protected host inventory mismatch")
    def api(method, params):
        return z.zabbix_api(token, method, params)

    STAGE = "read target host"
    hosts = api("host.get", {
        "filter": {"host": [NAME]},
        "output": ["hostid", "host", "status", "monitored_by"],
        "selectGroups": ["groupid", "name"],
        "selectParentTemplates": ["templateid", "host"],
    })
    if len(hosts) != 1:
        raise RuntimeError("Expected exactly one existing router-01")
    host = hosts[0]
    if str(host["hostid"]) != OLD_ID or str(host["status"]) != "0":
        raise RuntimeError("Unexpected router Zabbix host identity")
    group_links = host.get("groups") or []
    if len(group_links) != 1 or group_links[0].get("name") != GROUP:
        raise RuntimeError("Unexpected router Zabbix group")
    if str(host.get("monitored_by", "0")) != "0":
        raise RuntimeError("Unexpected proxy monitoring configuration")
    linked = {t["host"] for t in host.get("parentTemplates") or []}
    if linked != {PASSIVE}:
        raise RuntimeError("Router template assignments changed; refuse deletion")

    STAGE = "resolve target template and host group"
    templates = api("template.get", {
        "filter": {"host": [ACTIVE]},
        "output": ["templateid", "host"],
    })
    groups = api("hostgroup.get", {
        "filter": {"name": [GROUP]},
        "output": ["groupid", "name"],
    })
    if len(templates) != 1 or len(groups) != 1:
        raise RuntimeError("Unique active Linux template or host group missing")
    template_id = templates[0]["templateid"]
    group_id = groups[0]["groupid"]
    if group_links[0]["groupid"] != group_id:
        raise RuntimeError("Group ID does not match")

    plan = {"old_hostid": OLD_ID, "host": NAME, "old_linked": sorted(linked),
            "target_template_id": template_id, "target_group_id": group_id,
            "delete_history": True, "new_interfaces": []}
    fp = fingerprint(plan)
    print("TARGET: router-01 Zabbix hostid=10701 ONLY")
    print("ACTION: DELETE host and all Zabbix history/items/problems; CREATE new active-only host")
    print("NEW HOST: router-01; group=Homelab/Linux; template=Linux by Zabbix agent active")
    print("NEW INTERFACES: none (active-only)")
    print("BACKUP: none, explicitly requested")
    print("PLAN FINGERPRINT: " + fp)
    if not args.apply:
        print("AUDIT ONLY: no changes")
        return
    if args.approve_fingerprint != fp:
        raise RuntimeError("Fingerprint mismatch; no changes")

    # The host is recreated with exactly one standard active template.
    # If host creation fails after deletion, stop and inspect the host list.
    STAGE = "delete old router Zabbix host"
    api("host.delete", [OLD_ID])
    print("DELETED OLD ZABBIX HOST ID: " + OLD_ID)

    STAGE = "create clean router Zabbix host"
    created = api("host.create", {
        "host": NAME,
        "name": NAME,
        "status": 0,
        "groups": [{"groupid": group_id}],
        "templates": [{"templateid": template_id}],
        "interfaces": [],
    })
    new_ids = created.get("hostids") or []
    if len(new_ids) != 1 or str(new_ids[0]) == OLD_ID:
        raise RuntimeError("Unexpected Zabbix host.create result")

    STAGE = "verify recreated Zabbix host"
    verify = api("host.get", {
        "filter": {"host": [NAME]},
        "output": ["hostid", "host", "status"],
        "selectGroups": ["groupid"],
        "selectParentTemplates": ["templateid"],
        "selectInterfaces": ["interfaceid"],
    })
    if len(verify) != 1 or str(verify[0]["hostid"]) != str(new_ids[0]):
        raise RuntimeError("Recreated host identity verification failed")
    if str(verify[0]["status"]) != "0":
        raise RuntimeError("Recreated host not enabled")
    if {g["groupid"] for g in verify[0]["groups"]} != {group_id}:
        raise RuntimeError("Recreated host group mismatch")
    if {t["templateid"] for t in verify[0]["parentTemplates"]} != {template_id}:
        raise RuntimeError("Recreated host template mismatch")
    if verify[0].get("interfaces"):
        raise RuntimeError("Unexpected host interfaces")
    print("SUCCESS: recreated router-01 active-only; new hostid=" + str(new_ids[0]))
    print("NOTE: new items require time to begin delivering fresh values")
    print("No router/AP service, agent or nftables modifications performed")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # No raw API errors, tokens or tracebacks in logs.
        print("SAFE FAILURE: stage=" + STAGE + "; error_class=" + type(exc).__name__)
        sys.exit(1)
