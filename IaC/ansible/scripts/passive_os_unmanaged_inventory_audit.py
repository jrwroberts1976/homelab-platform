#!/usr/bin/env python3
"""READ-ONLY: compare discovered LAN IPs with existing Zabbix OS Facts.

Uses the already deployed management-report Zabbix API token. No scan, writes,
remote modifications, OS guessing or access to the router. An active-only
Zabbix host can match by canonical inventory hostname when no agent interface
is configured. Ambiguous matches stay unresolved, never unmanaged.
"""
import argparse
import ipaddress
import json
from pathlib import Path
import requests

DEFAULT_INVENTORY = "/var/lib/homelab-network-hosts/inventory.json"
DEFAULT_TOKEN = "/etc/homelab-management-report/zabbix-api-token"
DEFAULT_ZABBIX = "https://zabbix.home.jrwroberts.co.uk/api_jsonrpc.php"
OS_KEYS = {"system.sw.os.get", "system.sw.os[name]"}
MAX_INVENTORY = 5000


def normalize(name):
    return str(name or "").strip().lower().split(".")[0]


def zabbix_api(url, token, method, params):
    response = requests.post(
        url, headers={"Authorization": f"Bearer {token}",
                      "Content-Type": "application/json-rpc"},
        json={"jsonrpc": "2.0", "method": method, "params": params, "id": 1},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise RuntimeError(f"Zabbix {method} failed: {data['error'].get('message')}")
    return data["result"]


def compare(inventory, hosts, os_items):
    if not isinstance(inventory, dict) or len(inventory) > MAX_INVENTORY:
        raise ValueError("Invalid inventory")
    by_id = {}
    for h in hosts:
        hostid = str(h["hostid"])
        if h.get("status") != "0":  # disabled host is not authoritative
            continue
        ips = set()
        for interface in h.get("interfaces", []):
            if interface.get("useip") == "1":
                try:
                    ips.add(str(ipaddress.ip_address(interface["ip"])))
                except (KeyError, TypeError, ValueError):
                    pass
        by_id[hostid] = {"name": normalize(h.get("host")),
                         "ips": ips, "has_os": False}
    for item in os_items:
        hostid = str(item.get("hostid"))
        if (hostid in by_id and item.get("key_") in OS_KEYS and
                item.get("status") == "0" and item.get("state") == "0" and
                int(item.get("lastclock") or 0) > 0 and
                str(item.get("lastvalue") or "").strip()):
            by_id[hostid]["has_os"] = True

    result = {"zabbix_os_authoritative": [], "zabbix_without_os": [],
              "unmatched_inventory": [], "ambiguous": []}
    for ip, device in inventory.items():
        try:
            ipaddress.ip_address(ip)
        except (TypeError, ValueError):
            continue
        if not isinstance(device, dict):
            continue
        name = normalize(device.get("hostname"))
        # Never infer managed identity from a generic vendor, OS family or MAC.
        matches = [h for h in by_id.values() if ip in h["ips"] or
                   (name and h["name"] and name == h["name"])]
        if len(matches) > 1:
            group = "ambiguous"
        elif matches and matches[0]["has_os"]:
            group = "zabbix_os_authoritative"
        elif matches:
            group = "zabbix_without_os"
        else:
            group = "unmatched_inventory"
        result[group].append(ip)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventory", type=Path, default=Path(DEFAULT_INVENTORY))
    ap.add_argument("--token", type=Path, default=Path(DEFAULT_TOKEN))
    ap.add_argument("--zabbix-url", default=DEFAULT_ZABBIX)
    ap.add_argument(
        "--show-unmatched", action="store_true",
        help="List IP, hostname, MAC and online state for unmatched inventory only",
    )
    args = ap.parse_args()
    if args.inventory.stat().st_size > 5_000_000:
        raise ValueError("Inventory too large")
    inventory = json.loads(args.inventory.read_text())
    token = args.token.read_text().strip()
    if not token:
        raise RuntimeError("No Zabbix API token")
    hosts = zabbix_api(args.zabbix_url, token, "host.get", {
        "output": ["hostid", "host", "status"],
        "selectInterfaces": ["ip", "useip"],
    })
    items = zabbix_api(args.zabbix_url, token, "item.get", {
        "output": ["hostid", "key_", "status", "state", "lastclock", "lastvalue"],
        "filter": {"key_": sorted(OS_KEYS)},
    })
    groups = compare(inventory, hosts, items)
    print("=== EXISTING INVENTORY VS ZABBIX OS FACTS (READ ONLY) ===")
    for group in ("zabbix_os_authoritative", "zabbix_without_os",
                  "ambiguous", "unmatched_inventory"):
        print(group.upper() + "=" + str(len(groups[group])))
    print("TOTAL_CLASSIFIED=" + str(sum(len(x) for x in groups.values())))
    print("NOTE=Unmatched is not proven unmanaged; review identities before passive publication")
    if args.show_unmatched:
        print("=== UNMATCHED INVENTORY: REVIEW BEFORE SCANNING ===")
        for ip in sorted(groups["unmatched_inventory"], key=lambda ip: ipaddress.ip_address(ip)):
            entry = inventory[ip]
            hostname = str(entry.get("hostname") or "").replace("\\n", " ")[:100]
            mac = str(entry.get("mac") or "").replace("\\n", " ")[:40]
            online = bool(entry.get("online", False))
            print(f"IP={ip} HOSTNAME={hostname!r} MAC={mac!r} ONLINE={online}")
    # Routine output remains aggregate-only, without credentials or OS strings.


if __name__ == "__main__":
    main()
