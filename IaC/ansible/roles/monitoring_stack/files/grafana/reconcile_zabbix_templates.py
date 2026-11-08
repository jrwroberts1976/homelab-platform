#!/usr/bin/env python3
"""Reconcile standard Linux Zabbix templates for verified managed hosts.

Default is read-only. --apply links only missing Linux agent templates;
templates; does not unlink, replace, or reconfigure any existing templates,
hosts, agents, network or router services.
"""
import argparse
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

BUILDER = Path("/usr/local/sbin/homelab-grafana-zabbix-rebuild")
LINUX_PASSIVE = "Linux by Zabbix agent"
LINUX_ACTIVE = "Linux by Zabbix agent active"


def existing_builder():
    loader = SourceFileLoader("zabbix_dashboard_builder", str(BUILDER))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Add only missing templates (requires Zabbix API write permissions)")
    args = parser.parse_args()
    z = existing_builder()
    names, token, _ = z.read_secret_files()
    if len(names) != 15:
        raise RuntimeError("Expected 15 managed hosts; refusing incomplete inventory")
    all_hosts = z.zabbix_api(token, "host.get", {
        "output": ["hostid", "host", "name", "status"],
        "filter": {"status": "0"},
        "selectParentTemplates": ["templateid", "name", "host"],
        "selectInterfaces": ["type", "ip", "port", "main"],
        "limit": 1000,
    })
    templates = z.zabbix_api(token, "template.get", {
        "output": ["templateid", "host", "name"],
        "filter": {"host": [LINUX_PASSIVE, LINUX_ACTIVE]},
    })
    template_ids = {}
    for template_name in (LINUX_PASSIVE, LINUX_ACTIVE):
        matches = [t for t in templates if t.get("host") == template_name]
        if len(matches) != 1:
            raise RuntimeError("Exactly one " + template_name + " template required; no changes applied")
        template_ids[template_name] = matches[0]["templateid"]
    active_names = {LINUX_PASSIVE.lower(), LINUX_ACTIVE.lower()}
    planned = []
    print("MODE: " + ("APPLY" if args.apply else "AUDIT ONLY"))
    for name in names:
        hosts = [h for h in all_hosts if name in (h["host"], h["name"])]
        if len(hosts) != 1:
            raise RuntimeError("Missing or duplicate monitored host: " + name)
        h = hosts[0]
        linked = h.get("parentTemplates") or []
        existing = [t.get("name") or t.get("host") or "" for t in linked]
        linux = [t for t in existing if t.lower() in active_names]
        if linux:
            print(name + " | EXISTING Linux template: " + ", ".join(linux))
            continue
        # Guard against template collisions from custom Linux templates:
        # never automatically link if the host already has any other template.
        if linked:
            print(name + " | REVIEW: linked templates present: " + ", ".join(existing)
                  + " (no automatic change)")
            continue
        desired = LINUX_ACTIVE if name == "router-01" else LINUX_PASSIVE
        if desired == LINUX_PASSIVE:
            interfaces = [i for i in h.get("interfaces") or []
                          if str(i.get("type")) == "1" and str(i.get("port")) == "10050"]
            if not interfaces:
                print(name + " | REVIEW: missing agent interface (no automatic change)")
                continue
        # Active mode instead requires a matching Hostname and ServerActive
        # on the agent, already verified operationally for router-01.
        planned.append((name, h["hostid"], desired))
        print(name + " | PLAN: link " + desired)
    print("SUMMARY: " + str(len(names)) + " hosts inspected; "
          + str(len(planned)) + " safe new template links identified")
    if args.apply:
        for name, hostid, desired in planned:
            template_id = template_ids[desired]
            z.zabbix_api(token, "host.massadd", {
                "hosts": [{"hostid": hostid}],
                "templates": [{"templateid": template_id}],
            })
            verify = z.zabbix_api(token, "host.get", {
                "hostids": [hostid], "output": ["hostid"],
                "selectParentTemplates": ["templateid", "name"],
            })
            if len(verify) != 1 or template_id not in {
                t["templateid"] for t in verify[0]["parentTemplates"]
            }:
                raise RuntimeError("Template link verification failed for " + name)
            print("LINKED AND VERIFIED: " + name)
        print("APPLY COMPLETE: existing host templates preserved")
    else:
        print("No changes made; explicitly use --apply to add safe missing links")


if __name__ == "__main__":
    main()
