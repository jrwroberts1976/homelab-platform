#!/usr/bin/env python3
"""Audit and optionally clear Homelab Linux OS Facts links on managed hosts.

Scope: the 14 managed hosts other than router-01. Default read-only.
Preserves standard active template and other template links.
Does NOT delete the global template, edit host agents, or touch router/AP.
'Unlink and clear' deletes inherited Zabbix items and their history.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from importlib.machinery import SourceFileLoader

BUILDER = "/usr/local/sbin/homelab-grafana-zabbix-rebuild"
OLD = "Homelab Linux OS Facts"
ACTIVE = "Linux by Zabbix agent active"
EXCLUDE = "router-01"
STEP = "initialization"


def fingerprint(plan):
    return hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]


def main():
    global STEP
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true")
    p.add_argument("--approve-fingerprint", default="")
    args = p.parse_args()
    if args.apply and not args.approve_fingerprint:
        raise RuntimeError("Apply requires explicit plan fingerprint")

    STEP = "load existing Zabbix client"
    loader = SourceFileLoader("homelab_os_facts_cleanup", BUILDER)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    z = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z)
    names, token, _ = z.read_secret_files()
    if len(names) != 15 or EXCLUDE not in names or len(set(names)) != 15:
        raise RuntimeError("Managed inventory changed; refusing cleanup")
    desired = set(names) - {EXCLUDE}
    if len(desired) != 14:
        raise RuntimeError("Expected 14 non-router hosts")

    def api(method, params):
        return z.zabbix_api(token, method, params)

    STEP = "resolve legacy and standard templates"
    template_records = api("template.get", {
        "filter": {"host": [OLD, ACTIVE]},
        "output": ["templateid", "host", "name"],
    })
    by_host = {name: [t for t in template_records if t["host"] == name]
               for name in (OLD, ACTIVE)}
    if any(len(v) != 1 for v in by_host.values()):
        raise RuntimeError("Template identities ambiguous")
    old_id = by_host[OLD][0]["templateid"]
    active_id = by_host[ACTIVE][0]["templateid"]

    STEP = "inspect all managed Zabbix hosts"
    hosts = api("host.get", {
        "output": ["hostid", "host", "name", "status"],
        "selectParentTemplates": ["templateid", "host", "name"],
        "limit": 10000,
    })
    records = {}
    for name in names:
        matches = [h for h in hosts if h.get("host") == name]
        if len(matches) != 1 or str(matches[0].get("status")) != "0":
            raise RuntimeError("Missing, duplicate or disabled managed host: " + name)
        records[name] = matches[0]

    router_templates = {x["templateid"]
                        for x in (records[EXCLUDE].get("parentTemplates") or [])}
    if old_id in router_templates or active_id not in router_templates:
        raise RuntimeError("Router template state unexpectedly changed; refuse cleanup")

    STEP = "plan legacy template unlink-and-clear"
    changes = []
    print("SCOPE: 14 managed hosts except router-01; no router or AP changes")
    for name in sorted(desired):
        host = records[name]
        template_ids = {t["templateid"] for t in host.get("parentTemplates") or []}
        if active_id not in template_ids:
            raise RuntimeError("Active Linux monitoring missing from host " + name)
        if old_id in template_ids:
            preserved = sorted(template_ids - {old_id})
            changes.append({"name": name, "hostid": host["hostid"],
                            "linked_before": sorted(template_ids),
                            "preserved": preserved})
            print(name + ": REMOVE OS Facts link, KEEP " + str(len(preserved)) + " other template(s)")
        else:
            print(name + ": already clean; KEEP existing active Linux monitoring")

    plan = {"legacy_templateid": old_id, "active_templateid": active_id,
            "router_hostid": records[EXCLUDE]["hostid"],
            "changes": changes,
            "target_hosts": sorted(desired)}
    digest = fingerprint(plan)
    print("HOSTS TO CHANGE: " + str(len(changes)) + " / 14")
    print("PLAN FINGERPRINT: " + digest)
    print("WARNING: unlink-and-clear permanently removes legacy inherited items/history")
    print("GLOBAL TEMPLATE: retained; no global template deletion")
    if not args.apply:
        print("AUDIT ONLY: no Zabbix changes")
        return
    if args.approve_fingerprint != digest:
        raise RuntimeError("Plan changed since audit; refusing apply")

    for change in changes:
        STEP = "clear OS Facts from " + change["name"]
        # Explicitly supply the full set of preserved template relationships.
        # Clearing only the targeted old template removes its inherited items.
        api("host.update", {
            "hostid": change["hostid"],
            "templates": [{"templateid": tid} for tid in change["preserved"]],
            "templates_clear": [{"templateid": old_id}],
        })
        STEP = "verify templates for " + change["name"]
        verification = api("host.get", {
            "hostids": [change["hostid"]],
            "output": ["hostid", "host"],
            "selectParentTemplates": ["templateid"],
        })
        if len(verification) != 1 or verification[0].get("host") != change["name"]:
            raise RuntimeError("Post-change host verification failed")
        after = {t["templateid"] for t in verification[0].get("parentTemplates") or []}
        if after != set(change["preserved"]) or active_id not in after:
            raise RuntimeError("Post-change template verification failed")
        print("CLEARED AND VERIFIED: " + change["name"])

    STEP = "verify all 15 managed hosts unchanged except planned links"
    final = api("host.get", {
        "output": ["hostid", "host", "status"],
        "selectParentTemplates": ["templateid"],
        "limit": 10000,
    })
    by_name_final = {h["host"]: h for h in final if h["host"] in names}
    if len(by_name_final) != 15:
        raise RuntimeError("Final managed host count mismatch")
    for name in names:
        actual = {t["templateid"] for t in by_name_final[name].get("parentTemplates") or []}
        previous = {t["templateid"] for t in records[name].get("parentTemplates") or []}
        expected = previous - ({old_id} if name != EXCLUDE else set())
        if actual != expected:
            raise RuntimeError("Final template mismatch for " + name)
    print("SUCCESS: old OS Facts links cleared from requested managed hosts")
    print("Preserved: all 15 Zabbix hosts, Linux active templates, router-01 and global template")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("SAFE FAILURE: stage=" + STEP + "; error_class=" + type(exc).__name__)
        sys.exit(1)
