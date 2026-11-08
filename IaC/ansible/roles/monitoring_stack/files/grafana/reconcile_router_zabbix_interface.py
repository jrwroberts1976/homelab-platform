#!/usr/bin/env python3
"""Guarded router-01 Zabbix host-interface reconciliation.

Audit-only by default. --apply creates Zabbix-side agent interface only,
192.168.2.1:10050, and never accesses router or AP infrastructure.
No host template changes, service restarts, or firewall changes.
"""
import argparse
import importlib.util
import sys
from importlib.machinery import SourceFileLoader

BUILDER = "/usr/local/sbin/homelab-grafana-zabbix-rebuild"
ROUTER = "router-01"
EXPECTED_HOSTID = "10701"
EXPECTED = {"type": "1", "main": "1", "useip": "1",
            "ip": "192.168.2.1", "dns": "", "port": "10050"}
STEP = "initialization"


def main():
    global STEP
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    STEP = "load existing Zabbix API client"
    loader = SourceFileLoader("homelab_zabbix_router_interface_builder", BUILDER)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    z = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z)

    STEP = "verify managed host inventory"
    hostnames, token, _ = z.read_secret_files()
    if len(hostnames) != 15 or ROUTER not in hostnames:
        raise RuntimeError("Protected host inventory changed")

    STEP = "read router host and interfaces"
    hosts = z.zabbix_api(token, "host.get", {
        "filter": {"host": [ROUTER]},
        "output": ["hostid", "host", "status"],
        "selectInterfaces": ["interfaceid", "type", "main", "useip", "ip", "dns", "port"],
    })
    if (len(hosts) != 1 or
            str(hosts[0]["hostid"]) != EXPECTED_HOSTID or
            str(hosts[0]["status"]) != "0"):
        raise RuntimeError("Unexpected router-01 Zabbix host")
    host = hosts[0]
    interfaces = host.get("interfaces") or []
    if len(interfaces) == 1 and all(
        str(interfaces[0].get(key, "")) == value for key, value in EXPECTED.items()
    ):
        print("INTERFACE VERIFIED: router-01 Agent IP 192.168.2.1:10050")
        return
    if interfaces:
        raise RuntimeError("Existing interfaces differ; refusing to modify or duplicate")

    print("PRECHECK PASS: router-01 host 10701 has no interfaces")
    print("PROPOSED: create one Zabbix Agent interface, IP 192.168.2.1 port 10050")
    if not args.apply:
        print("AUDIT ONLY: no changes")
        return

    STEP = "create Zabbix host interface"
    z.zabbix_api(token, "hostinterface.create", {
        "hostid": host["hostid"],
        **{key: int(value) if key in ("type", "main", "useip") else value
           for key, value in EXPECTED.items()},
    })
    STEP = "verify created Zabbix host interface"
    verify = z.zabbix_api(token, "host.get", {
        "hostids": [host["hostid"]],
        "output": ["hostid"],
        "selectInterfaces": ["interfaceid", "type", "main", "useip", "ip", "dns", "port"],
    })
    if len(verify) != 1 or len(verify[0].get("interfaces") or []) != 1 or not all(
        str(verify[0]["interfaces"][0].get(key, "")) == value
        for key, value in EXPECTED.items()
    ):
        raise RuntimeError("Post-creation Zabbix host-interface validation failed")
    print("INTERFACE CREATED AND VERIFIED: router-01 192.168.2.1:10050")
    print("No templates or router/AP configuration were changed")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("SAFE FAILURE: stage=" + STEP + "; error_class=" + type(exc).__name__)
        sys.exit(1)
