#!/usr/bin/env python3
"""Publish a privacy-minimised, evidence-qualified, MAC/IP network inventory.

Source precedence: documented OS > dated DNS inference > Nmap OS guess.
Port results are observations from limited scans, never proof other ports are shut.
Read-only inputs: Prometheus, the router asset DB, curated IaC, Nmap baselines.
"""
from collections import Counter
import hashlib
import ipaddress
import json
import os
import re
import sqlite3
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

PROMETHEUS = "http://127.0.0.1:9090/api/v1/query"
ESTATE = Path("/etc/homelab/network-estate.json")
DNS_HINTS = Path("/etc/homelab/network-device-dns-hints.json")
ROUTER_DB = Path("/var/lib/asus-network-inventory/assets.db")
BASELINE_ROOT = Path("/var/lib/homelab-os-baselines")
OUTPUT = Path("/var/lib/prometheus/node-exporter/homelab_network_devices.prom")
LAN = ipaddress.ip_network("192.168.2.0/24")


def lan_ip(value):
    try:
        addr = ipaddress.ip_address(str(value))
        return str(addr) if addr in LAN else None
    except ValueError:
        return None


def esc(value):
    return (str(value or "").replace("\\", "\\\\")
            .replace('"', '\\"').replace("\r", " ").replace("\n", " "))[:520]


def labels(fields):
    return ",".join('%s="%s"' % (key, esc(value))
                    for key, value in fields.items())


def prometheus(expr):
    url = PROMETHEUS + "?" + urlencode({"query": expr})
    with urlopen(url, timeout=12) as response:
        payload = json.load(response)
    if payload.get("status") != "success":
        raise RuntimeError("Prometheus rejected query: " + expr)
    return payload.get("data", {}).get("result", [])


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def router_inventory():
    if not ROUTER_DB.is_file():
        return []
    connection = sqlite3.connect(
        "file:" + str(ROUTER_DB) + "?mode=ro", uri=True, timeout=8)
    try:
        rows = connection.execute(
            "SELECT ip,mac,hostname,last_seen,online FROM assets"
        ).fetchall()
    finally:
        connection.close()
    return [{"ip": ip, "mac": mac, "hostname": hostname,
             "last_seen": last_seen, "online": online} for
            ip, mac, hostname, last_seen, online in rows]


def latest_baseline():
    candidates = sorted(BASELINE_ROOT.glob("*/baseline.json"), reverse=True)
    if not candidates:
        return {}, set(), ""
    path = candidates[0]
    scan_stamp = path.parent.name
    data = load_json(path)
    results = {item["ip"]: item for item in data
               if isinstance(item, dict) and lan_ip(item.get("ip"))}
    log_path = path.parent / "scan.log"
    timeouts = set()
    if log_path.exists():
        timeouts = set(re.findall(
            r"Skipping host ([0-9.]+) due to host timeout",
            log_path.read_text(encoding="utf-8", errors="replace")))
    return results, timeouts, scan_stamp


def populate():
    estate = load_json(ESTATE)
    dns = load_json(DNS_HINTS)
    hosts = {}

    def host(ip):
        ip = lan_ip(ip)
        if ip is None:
            return None
        if ip not in hosts:
            hosts[ip] = dict(ip=ip, mac="", hostname="", vendor="",
                             kind="", role="", os="Unknown",
                             os_source="Not determined",
                             os_evidence="unknown", dns_hint="",
                             dns_observed="", online=None, last_seen=0,
                             ports={}, scan_timed_out=False)
        return hosts[ip]

    # Documented infrastructure is included even when temporarily offline.
    for asset in estate.get("assets", []):
        if asset.get("state") != "active":
            continue
        h = host(asset.get("address"))
        if h is None:
            continue
        h["hostname"] = asset.get("document_label") or asset.get("name") or ""
        h["role"] = asset.get("role") or ""
        h["kind"] = asset.get("kind") or ""
        name = asset.get("name")
        if name == "home-01":
            h.update(os="Home Assistant OS 18.2",
                     os_source="Canonical estate (2026-09)",
                     os_evidence="documented")
        elif name in ("PROXMOX", "Proxmox-2"):
            h.update(os="Proxmox VE / Debian",
                     os_source="Canonical estate (2026-09)",
                     os_evidence="documented")
        elif asset.get("managed_by_ansible"):
            h.update(os="Linux (IaC-managed)",
                     os_source="Canonical estate (2026-09)",
                     os_evidence="documented")

    # Core Nmap discovery and the existing router asset publisher.
    for result in prometheus("homelab_network_host_info"):
        m = result.get("metric", {})
        h = host(m.get("ip"))
        if h is None:
            continue
        for field in ("mac", "vendor"):
            if m.get(field) and not h[field]:
                h[field] = m[field]
        if m.get("hostname") and not h["hostname"]:
            h["hostname"] = m["hostname"]

    for result in prometheus("asus_network_asset_info"):
        m = result.get("metric", {})
        h = host(m.get("ip"))
        if h is None:
            continue
        for field in ("mac", "hostname"):
            if m.get(field) and not h[field]:
                h[field] = m[field]

    # Preserve historical ASUS records, not just the current Prometheus view.
    for item in router_inventory():
        h = host(item.get("ip"))
        if h is None:
            continue
        for field in ("mac", "hostname"):
            if item.get(field) and not h[field]:
                h[field] = item[field]
        h["last_seen"] = max(
            h["last_seen"], int(item.get("last_seen") or 0))

    for metric_name in ("homelab_network_host_up", "asus_network_asset_up"):
        for result in prometheus(metric_name):
            m = result.get("metric", {})
            h = host(m.get("ip"))
            if h is None:
                continue
            up = float(result["value"][1]) == 1
            h["online"] = bool(h["online"]) or up if h["online"] is not None else up

    for metric_name in ("homelab_network_host_last_seen_seconds",
                        "asus_network_asset_last_seen_seconds"):
        for result in prometheus(metric_name):
            h = host(result.get("metric", {}).get("ip"))
            if h is not None:
                h["last_seen"] = max(
                    h["last_seen"], int(float(result["value"][1])))

    # Dated DNS evidence is a hint, never a verified operating system.
    for ip, evidence in dns.get("devices", {}).items():
        h = host(ip)
        if h is None:
            continue
        h["dns_hint"] = evidence.get("dns_hint", "")
        h["dns_observed"] = dns.get("observed_on", "")
        if h["os_evidence"] == "unknown" and evidence.get("os_hint"):
            h.update(os=evidence["os_hint"], os_source="Pi-hole DNS snapshot",
                     os_evidence="inferred_dns")

    baseline, timeouts, stamp = latest_baseline()
    for ip, entry in baseline.items():
        h = host(ip)
        if h is None:
            continue
        h["scan_timed_out"] = ip in timeouts
        if ip in timeouts or entry.get("scan_status") != "up":
            continue
        matches = entry.get("os_matches") or []
        if matches and h["os_evidence"] == "unknown":
            best = max(matches, key=lambda x: float(
                x.get("accuracy_percent", x.get("accuracy", 0)) or 0))
            h.update(os=best.get("name") or "Unknown",
                     os_source="Nmap guess " + stamp[:8],
                     os_evidence="inferred_nmap")
        for p in entry.get("ports", []):
            if p.get("state") != "open":
                continue
            try:
                port = int(p["port"])
            except (ValueError, KeyError, TypeError):
                continue
            protocol = p.get("protocol") or "tcp"
            service = p.get("service") or ""
            if isinstance(service, dict):
                service = service.get("name") or ""
            h["ports"][(protocol, port)] = {
                "protocol": protocol, "port": port,
                "service": service, "product": p.get("product") or "",
                "version": p.get("version") or "", "source": "Nmap top-100",
                "observed": stamp[:8]}

    # Prefer the existing regularly refreshed, selected-port enrichment data.
    for result in prometheus("homelab_network_host_enrichment_port_info"):
        m = result.get("metric", {})
        h = host(m.get("ip"))
        if h is None:
            continue
        try:
            port = int(m["port"])
        except (ValueError, KeyError, TypeError):
            continue
        protocol = m.get("protocol") or "tcp"
        h["ports"][(protocol, port)] = {
            "protocol": protocol, "port": port,
            "service": m.get("service") or "",
            "product": m.get("product") or "",
            "version": m.get("version") or "",
            "source": "Selected-port enrichment", "observed": ""}

    return hosts


def render(hosts):
    lines = [
        "# HELP homelab_network_device_inventory_info Correlated LAN device inventory with evidence-qualified OS and observed ports.",
        "# TYPE homelab_network_device_inventory_info gauge",
        "# HELP homelab_network_device_online Most recently published discovery/router presence; -1 means unknown.",
        "# TYPE homelab_network_device_online gauge",
        "# HELP homelab_network_device_last_seen_seconds Last available observation (UNIX time).",
        "# TYPE homelab_network_device_last_seen_seconds gauge",
        "# HELP homelab_network_device_open_port_info Observed open port in selected scans, not full-port coverage.",
        "# TYPE homelab_network_device_open_port_info gauge",
        "# HELP homelab_network_device_open_ports_total Observed open ports; absent evidence is not zero.",
        "# TYPE homelab_network_device_open_ports_total gauge",
        "# HELP homelab_network_device_inventory_last_run_seconds Last successful source-correlation run.",
        "# TYPE homelab_network_device_inventory_last_run_seconds gauge",
        "# HELP homelab_network_device_card_info One current MAC-keyed identity, or an IP fallback when MAC is unavailable.",
        "# TYPE homelab_network_device_card_info gauge",
        "# HELP homelab_network_device_card_online Current device presence by stable device key; -1 unknown.",
        "# TYPE homelab_network_device_card_online gauge",
        "# HELP homelab_network_device_card_last_seen_seconds Last known observation of the MAC-keyed device.",
        "# TYPE homelab_network_device_card_last_seen_seconds gauge",
        "# HELP homelab_network_device_card_port_info Positively observed open service port for the device's current known address.",
        "# TYPE homelab_network_device_card_port_info gauge",
    ]
    for ip in sorted(hosts, key=lambda s: ipaddress.ip_address(s)):
        h = hosts[ip]
        ports = sorted(h["ports"].values(),
                       key=lambda p: (p["protocol"], p["port"]))
        summary = ", ".join(
            "%s/%s %s" % (p["port"], p["protocol"], p["service"] or "unknown")
            for p in ports)
        if len(summary) > 480:
            summary = summary[:475] + " ..."
        if not ports:
            summary = ("Not assessed (scan timed out)" if h["scan_timed_out"]
                       else "No open ports evidenced")
        status = ("Unknown" if h["online"] is None
                  else "Online" if h["online"] else "Offline")
        info = {key: h[key] for key in
                ("ip", "mac", "hostname", "vendor", "kind", "role",
                 "os", "os_source", "os_evidence", "dns_hint", "dns_observed")}
        info.update(status=status, observed_open_ports=summary)
        lines.append("homelab_network_device_inventory_info{" +
                     labels(info) + "} 1")
        lines.append("homelab_network_device_online{" +
                     labels({"ip": ip}) + "} " +
                     str(-1 if h["online"] is None
                         else int(h["online"])))
        if h["last_seen"]:
            lines.append("homelab_network_device_last_seen_seconds{" +
                         labels({"ip": ip}) + "} " + str(h["last_seen"]))
        if ports:
            lines.append("homelab_network_device_open_ports_total{" +
                         labels({"ip": ip}) + "} " + str(len(ports)))
        for p in ports:
            fields = {"ip": ip, "port": p["port"],
                      "protocol": p["protocol"],
                      "service": p["service"],
                      "product": p["product"],
                      "version": p["version"],
                      "source": p["source"],
                      "observed": p["observed"]}
            lines.append("homelab_network_device_open_port_info{" +
                         labels(fields) + "} 1")
    # The card view follows each device by MAC instead of creating another tile
    # when its IP changes. A documented host without an observed MAC retains
    # a clearly marked IP fallback until a MAC can be correlated.
    cards = {}
    valid_mac = re.compile(r"^(?:[0-9a-f]{2}:){5}[0-9a-f]{2}$")
    for ip, h in hosts.items():
        mac = str(h.get("mac") or "").strip().lower().replace("-", ":")
        device_key = "mac:" + mac if valid_mac.fullmatch(mac) else "ip:" + ip
        old = cards.get(device_key)
        freshness = (
            1 if h.get("online") is True else 0,
            int(h.get("last_seen") or 0),
            1 if h.get("os_evidence") == "documented" else 0,
        )
        if old is None or freshness > old[0]:
            cards[device_key] = (freshness, h)

    name_counts = Counter(
        (entry[1].get("hostname") or "").strip().casefold()
        for entry in cards.values()
        if (entry[1].get("hostname") or "").strip()
    )
    for device_key in sorted(cards):
        h = cards[device_key][1]
        ip = h["ip"]
        mac = (str(h.get("mac") or "").strip().lower()
               .replace("-", ":"))
        if not valid_mac.fullmatch(mac):
            mac = ""
        # User-facing Grafana names are hostnames. Fall back to IP rather
        # than raw MAC or generic vendor if DHCP/reverse DNS cannot name it.
        name = (h.get("hostname") or "").strip()
        display_name = name or ip
        if name and name_counts[name.casefold()] > 1:
            display_name = "%s (%s)" % (name, ip)
        dashboard_uid = (
            "net-host-" + hashlib.sha256(
                device_key.encode("utf-8")).hexdigest()[:12]
        )
        ports = sorted(
            h["ports"].values(),
            key=lambda p: (p["protocol"], p["port"]),
        )
        summary = ", ".join(
            "%s/%s %s" % (p["port"], p["protocol"],
                         p["service"] or "unknown")
            for p in ports
        )[:480]
        if not ports:
            summary = (
                "Not assessed (scan timed out)" if h["scan_timed_out"]
                else "No open ports evidenced"
            )
        status = (
            "Unknown" if h["online"] is None
            else "Online" if h["online"] else "Offline"
        )
        common = {
            "device_key": device_key,
            "ip": ip,
            "mac": mac,
            "hostname": display_name,
            "os": h["os"],
            "os_evidence": h["os_evidence"],
            "dashboard_uid": dashboard_uid,
        }
        info = {
            **common,
            "vendor": h["vendor"],
            "role": h["role"],
            "kind": h["kind"],
            "os_source": h["os_source"],
            "dns_hint": h["dns_hint"],
            "dns_observed": h["dns_observed"],
            "observed_open_ports": summary,
            "status": status,
        }
        lines.append(
            "homelab_network_device_card_info{" +
            labels(info) + "} 1"
        )
        lines.append(
            "homelab_network_device_card_online{" +
            labels(common) + "} " +
            str(-1 if h["online"] is None else int(h["online"]))
        )
        if h["last_seen"]:
            lines.append(
                "homelab_network_device_card_last_seen_seconds{" +
                labels({"device_key": device_key}) + "} " +
                str(int(h["last_seen"]))
            )
        for port in ports:
            fields = {
                "device_key": device_key,
                "ip": ip,
                "port": port["port"],
                "protocol": port["protocol"],
                "service": port["service"],
                "product": port["product"],
                "version": port["version"],
                "source": port["source"],
                "observed": port["observed"],
            }
            lines.append(
                "homelab_network_device_card_port_info{" +
                labels(fields) + "} 1"
            )

    lines.append("homelab_network_device_inventory_last_run_seconds %d" %
                 int(time.time()))
    return "\n".join(lines) + "\n"


def main():
    hosts = populate()
    if len(hosts) < 10:
        raise RuntimeError("Safety gate: fewer than 10 LAN assets; retaining last good metrics")
    data = render(hosts)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=".homelab_network_devices_", suffix=".prom",
        dir=str(OUTPUT.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, OUTPUT)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print("Published %d assets and %d observed open ports" %
          (len(hosts), sum(len(h["ports"]) for h in hosts.values())))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Inventory publication failed; last good metrics retained: %s" %
              exc, file=sys.stderr)
        sys.exit(1)
