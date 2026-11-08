#!/usr/bin/env python3
"""Read-only Zabbix 7 audit of OS and patch telemetry for managed hosts.

Loads the same protected API configuration as the Grafana Zabbix dashboard
builder. No package installation, package refresh, Zabbix writes or Grafana writes.
"""
import importlib.util
from importlib.machinery import SourceFileLoader
import json
import re
import time
from pathlib import Path

BUILDER = Path("/usr/local/sbin/homelab-grafana-zabbix-rebuild")
# These are *potential* update/compliance items, not installed-package discovery.
# Never classify system.sw.packages.get as patch coverage.
PATTERNS = {
    "pending_updates": re.compile(r"(?:pending|available|outstanding|upgradable|updates\\.count|upgrade\\.count)", re.I),
    "security_updates": re.compile(r"(?:security[_ .-]*(?:patch|update|upgrade)|(?:patch|update|upgrade)[_ .-]*security|cve\\.)", re.I),
    "reboot_required": re.compile(r"(?:reboot[_ .-]*required|restart[_ .-]*required|needs[_ .-]*restarting)", re.I),
    "last_patched": re.compile(r"(?:last[_ .-]*(?:patch|updated|upgraded)|patch[_ .-]*(?:date|timestamp))", re.I),
}
PACKAGE_DISCOVERY_KEYS = {"system.sw.packages.get"}
OS_KEYS = re.compile(r"^(?:system\.sw\.os(?:\[.*\])?|system\.uname)$", re.I)


def module():
    if not BUILDER.is_file():
        raise RuntimeError("Zabbix-first dashboard builder not installed")
    loader = SourceFileLoader("homelab_zabbix_dashboard", str(BUILDER))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load existing trusted dashboard builder")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    z = module()
    names, token, _ = z.read_secret_files()
    hosts = z.zabbix_api(token, "host.get", {
        "output": ["hostid", "host", "name", "status"],
        "selectInventory": ["os", "os_full"],
        "filter": {"status": "0"},
        "limit": 1000,
    })
    now = int(time.time())
    report = []
    for inventory_name in names:
        matches = [h for h in hosts if inventory_name in (h.get("host"), h.get("name"))]
        if len(matches) != 1:
            raise RuntimeError("Host not uniquely enabled in Zabbix: " + inventory_name)
        host = matches[0]
        items = z.zabbix_api(token, "item.get", {
            "hostids": host["hostid"],
            "output": ["name", "key_", "status", "state", "value_type",
                       "lastvalue", "lastclock", "error"],
            "limit": 10000,
        })
        osinfo = z.os_details(host, items)
        os_candidates = []
        patch_candidates = []
        for item in items:
            key = item.get("key_", "")
            item_name = item.get("name", "")
            is_os = bool(OS_KEYS.search(key))
            groups = [] if key in PACKAGE_DISCOVERY_KEYS else [
                kind for kind, regex in PATTERNS.items()
                if regex.search(key) or regex.search(item_name)
            ]
            if not is_os and not groups:
                continue
            lastclock = int(item.get("lastclock") or 0)
            age_hours = round((now - lastclock) / 3600, 1) if lastclock else None
            summary = {
                "key": key[:160],
                "name": item_name[:160],
                "enabled": item.get("status") == "0",
                "supported": item.get("state") == "0",
                "has_value": bool(lastclock),
                "age_hours": age_hours,
                "value": str(item.get("lastvalue") or "")[:120],
            }
            if is_os:
                os_candidates.append(summary)
            if groups:
                summary["categories"] = groups
                patch_candidates.append(summary)
        # Surface only actual Zabbix item definitions. A name match is a
        # candidate, never proof the host has patch compliance coverage.
        report.append({
            "host": inventory_name,
            "os": osinfo,
            "os_item_candidates": os_candidates,
            "patch_item_candidates": patch_candidates,
            "patch_telemetry_confirmed": False,
        })
    output = {
        "mode": "READ_ONLY",
        "note": "Package inventory discovery is excluded. Patch candidates are unverified; compliance is Unknown for all hosts.",
        "hosts_checked": len(report),
        "hosts_with_os": sum(not x["os"]["os"].startswith("Unknown") for x in report),
        "hosts_with_patch_candidates": sum(bool(x["patch_item_candidates"]) for x in report),
        "hosts_with_verified_patch_compliance": 0,
        "hosts": report,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
