#!/usr/bin/env python3
"""No-send, read-only router DHCP candidate and enrichment policy.

The existing network collector remains the SOLE SMTP sender, and its
alerted-macs.json stays the single MAC-level notification ledger.
Only a separately approved marker enables this DHCP source.

Do not import private DNS logs, scan the LAN, or create Grafana dashboards.
"""
import hashlib
import ipaddress
import json
import re
import time
from pathlib import Path

LAN = ipaddress.IPv4Network("192.168.2.0/24")
MAC = re.compile(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\Z")
MAX_PENDING = 10
GRAFANA_URL = "https://grafana.home.jrwroberts.co.uk"
MAX_AGE_NS = 48 * 3600 * 10**9
FUTURE_SLACK_NS = 300 * 10**9


def read_json(path):
    file = Path(path)
    if file.is_symlink() or not file.is_file():
        raise ValueError("Protected device notification data is absent/unsafe")
    return json.loads(file.read_text(encoding="utf-8"))


def identity(mac, ip):
    if not isinstance(mac, str) or MAC.fullmatch(mac) is None:
        return False
    if int(mac[:2], 16) & 1 or mac == "00:00:00:00:00:00":
        return False
    try:
        address = ipaddress.IPv4Address(ip)
    except (ipaddress.AddressValueError, ValueError, TypeError):
        return False
    return address in LAN and str(address) not in ("192.168.2.1", "192.168.2.255")


def uid_for(mac):
    return "routerdhcp-" + hashlib.sha256(mac.encode("ascii")).hexdigest()[:20]


def display(value, length=100):
    text = str(value or "").replace("\r", " ").replace("\n", " ")
    for x in ("\u0000", "<", ">", "|", chr(96)):
        text = text.replace(x, " ")
    return " ".join(text.split())[:length]


def os_evidence(mac, ip, profiles):
    rec = profiles.get(mac)
    if not isinstance(rec, dict) or rec.get("profiled_ip") != ip:
        return "Pending identification"
    profile = rec.get("profile", {})
    tcp = profile.get("tcp", {}) if isinstance(profile, dict) else {}
    matches = tcp.get("os_matches", []) if isinstance(tcp, dict) else []
    if not isinstance(matches, list) or not matches or not isinstance(matches[0], dict):
        return "Pending identification"
    first = matches[0]
    name = display(first.get("name"), 100)
    if not name:
        return "Pending identification"
    score = str(first.get("accuracy") or "")
    if score.isdecimal() and int(score) <= 100:
        return f"Nmap inferred: {name} (match score {score}%)"
    return "Nmap inferred: " + name


def candidates(state, marker, already_known, inventory, profiles, source_dir, now_ns=None):
    """Return up to MAX_PENDING new DHCP MACs, without writing/sending anything.

    MACs already registered by the original discovery notifier NEVER re-alert.
    DHCP first-seen timestamps on/before activation are historical (no backlog).
    Page source must exist before a candidate is eligible for an email link.
    """
    if now_ns is None:
        now_ns = time.time_ns()
    if not isinstance(marker, dict) or marker.get("schema_version") != 1:
        raise ValueError("Unapproved DHCP-email activation state")
    start = marker.get("activated_at_ns")
    if not isinstance(start, int) or not 0 < start <= now_ns + FUTURE_SLACK_NS:
        raise ValueError("Invalid DHCP-email activation time")
    if (not isinstance(state, dict) or state.get("schema_version") != 1
            or not isinstance(state.get("devices"), dict)):
        raise ValueError("DHCP device page state is invalid")
    devices = state["devices"]
    if len(devices) > 254 or not isinstance(profiles, dict) or not isinstance(inventory, dict):
        raise ValueError("DHCP identity/profile input exceeds bounds or invalid")
    if not isinstance(already_known, (set, dict)):
        raise ValueError("Missing shared MAC notification history")
    source_dir = Path(source_dir)
    if source_dir.is_symlink() or not source_dir.is_dir():
        raise ValueError("Unsafe Grafana device provider directory")
    pending = []
    for mac, record in sorted(devices.items()):
        if mac in already_known:
            continue
        if not isinstance(record, dict) or not identity(mac, record.get("ip")):
            raise ValueError("Invalid DHCP device MAC/IP in trusted state")
        first, last = record.get("first_seen_ns"), record.get("last_seen_ns")
        if not isinstance(first, int) or not isinstance(last, int):
            raise ValueError("Invalid DHCP observation timestamps")
        if not 0 < first <= last <= now_ns + FUTURE_SLACK_NS:
            raise ValueError("Invalid DHCP timestamp sequence")
        if first <= start or last < now_ns - MAX_AGE_NS:
            continue
        uid = uid_for(mac)
        path = source_dir / (uid + ".json")
        if path.is_symlink() or not path.is_file():
            continue
        dashboard = read_json(path)
        if not isinstance(dashboard, dict) or dashboard.get("uid") != uid:
            raise ValueError("DHCP page source UID mismatch")
        ip = record["ip"]
        # The original sole SMTP notifier passes normalise_inventory(),
        # which is MAC-keyed (not IP-keyed). Correlate both identity and the
        # current DHCP address to avoid stale vendor/online evidence.
        host = inventory.get(mac, {})
        if (not isinstance(host, dict)
                or str(host.get("mac", "")).lower() != mac
                or str(host.get("ip", "")) != ip):
            host = {}
        pending.append({
            "mac": mac,
            "ip": ip,
            "hostname": display(record.get("hostname"), 80),
            "vendor": display(host.get("vendor"), 80),
            "first_seen": first // 10**9,
            "last_seen": last // 10**9,
            "online": bool(host.get("online", False)),
            "source": "router-01 DHCPACK",
            "os_evidence": os_evidence(mac, ip, profiles),
            "dashboard_url": GRAFANA_URL + "/d/" + uid,
        })
        if len(pending) >= MAX_PENDING:
            break
    return pending


def from_files(state_file, marker_file, registry, inventory, profiles_file, source_dir,
               *, now_ns=None):
    """Fail closed on source damage; do not silently re-seed the MAC registry."""
    state = read_json(state_file)
    marker = read_json(marker_file)
    saved = read_json(profiles_file)
    profiles = saved.get("profiles") if isinstance(saved, dict) else None
    if not isinstance(profiles, dict):
        raise ValueError("Malformed protected Nmap profile state")
    known = registry.get("devices") if isinstance(registry, dict) else None
    if not isinstance(known, dict):
        raise ValueError("Malformed shared first-seen registry")
    return candidates(state, marker, known, inventory, profiles, source_dir, now_ns=now_ns)
