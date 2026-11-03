#!/usr/bin/env python3
"""MAC-stable Grafana pages sourced only from router-01 dnsmasq DHCPACK Loki logs.

Uses existing monitor-01 Nmap profiles; does NOT scan, email, delete pages,
alter router DHCP, or write to Grafana's API.
"""
import argparse
import fcntl
import hashlib
import ipaddress
import json
import os
import re
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SUBNET = ipaddress.IPv4Network("192.168.2.0/24")
MAC_RE = re.compile(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\Z")
DHCP_RE = re.compile(
    r"(?:^|:\s+|\s)DHCPACK\(eth0\)\s+"
    r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+"
    r"(?P<mac>(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})"
    r"(?:\s+(?P<hostname>[A-Za-z0-9_.-]{1,80}))?(?:\s|$)"
)
LOKI_LIMIT = 3000
MAX_DEVICES = 254


def clean_mac(value):
    mac = str(value or "").lower()
    if not MAC_RE.fullmatch(mac):
        return None
    octets = bytes.fromhex(mac.replace(":", ""))
    if (octets[0] & 1) or not any(octets):
        return None
    return mac


def parse_ack(line, timestamp_ns):
    match = DHCP_RE.search(str(line))
    if not match:
        return None
    mac = clean_mac(match.group("mac"))
    if not mac:
        return None
    try:
        ip = ipaddress.IPv4Address(match.group("ip"))
        seen_ns = int(timestamp_ns)
    except (ValueError, TypeError):
        return None
    if (ip not in SUBNET or ip in (SUBNET.network_address, SUBNET.broadcast_address)
            or str(ip) == "192.168.2.1" or seen_ns <= 0):
        return None
    return {"mac": mac, "ip": str(ip),
            "hostname": match.group("hostname") or "", "seen_ns": seen_ns}


def read_loki(url, now_ns):
    params = urllib.parse.urlencode({
        "query": '{host="router-01",service="dnsmasq"} |= "DHCPACK"',
        "start": str(now_ns - 36 * 3600 * 10**9), "end": str(now_ns),
        "direction": "backward", "limit": str(LOKI_LIMIT)})
    request = urllib.request.Request(
        url.rstrip("/") + "/loki/api/v1/query_range?" + params,
        headers={"Accept": "application/json"}, method="GET")
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read(4_000_000))
    data = payload.get("data", {})
    if payload.get("status") != "success" or data.get("resultType") != "streams":
        raise ValueError("Unexpected router DHCP Loki response")
    raw = []
    for stream in data.get("result", []):
        labels = stream.get("stream", {})
        if labels.get("host") != "router-01" or labels.get("service") != "dnsmasq":
            raise ValueError("Unexpected DHCP log source labels")
        for value in stream.get("values", []):
            if isinstance(value, list) and len(value) == 2:
                raw.append(value)
    if len(raw) >= LOKI_LIMIT:
        raise ValueError("DHCPACK query reached bounded-event safety limit")
    return [event for timestamp, line in raw
            if (event := parse_ack(line, timestamp)) is not None]


def read_json(path, *, optional=False):
    if path.is_symlink():
        raise ValueError("Symlink evidence path refused")
    if not path.exists():
        if optional:
            return None
        raise ValueError("Required local evidence missing")
    if not path.is_file():
        raise ValueError("Evidence must be regular file")
    return json.loads(path.read_text(encoding="utf-8"))


def load_state(path):
    raw = read_json(path, optional=True)
    if raw is None:
        return {"schema_version": 1, "devices": {}}
    if (not isinstance(raw, dict) or raw.get("schema_version") != 1
            or not isinstance(raw.get("devices"), dict)
            or len(raw["devices"]) > MAX_DEVICES):
        raise ValueError("Invalid persisted DHCP device page state")
    for mac, item in raw["devices"].items():
        if clean_mac(mac) != mac or not isinstance(item, dict):
            raise ValueError("Invalid persisted client MAC")
        if not parse_ack(
                "DHCPACK(eth0) " + str(item.get("ip", "")) + " " + mac,
                item.get("last_seen_ns")):
            raise ValueError("Invalid persisted DHCP client address")
    return raw


def merge_events(state, events, max_new=None):
    devices = {mac: dict(item) for mac, item in state["devices"].items()}
    count = 0
    for event in sorted(events, key=lambda x: (x["seen_ns"], x["mac"])):
        mac = event["mac"]
        if mac not in devices:
            if max_new is not None and count >= max_new:
                continue
            if len(devices) >= MAX_DEVICES:
                raise ValueError("Maximum DHCP device count exceeded")
            devices[mac] = {
                "first_seen_ns": event["seen_ns"],
                "last_seen_ns": event["seen_ns"],
                "ip": event["ip"],
                "hostname": event["hostname"],
            }
            count += 1
        elif event["seen_ns"] >= int(devices[mac].get("last_seen_ns", 0)):
            devices[mac]["ip"] = event["ip"]
            devices[mac]["last_seen_ns"] = event["seen_ns"]
            if event["hostname"]:
                devices[mac]["hostname"] = event["hostname"]
    return {"schema_version": 1, "devices": devices}, count


def safe_text(value, size=120):
    value = str(value or "").replace("\r", " ").replace("\n", " ")
    for char in ("|", chr(96), "<", ">", "[", "]", "\\"):
        value = value.replace(char, " ")
    return " ".join(value.split())[:size]


def os_and_ports(mac, ip, profiles):
    records = profiles.get("profiles", {})
    if not isinstance(records, dict):
        raise ValueError("Unexpected Nmap profile schema")
    entry = records.get(mac)
    if not isinstance(entry, dict) or entry.get("profiled_ip") != ip:
        return "Unknown — awaiting Nmap on this DHCP IP", "pending", []
    evidence = entry.get("profile", {})
    tcp = evidence.get("tcp", {}) if isinstance(evidence, dict) else {}
    if not isinstance(tcp, dict):
        return "Unknown — incomplete Nmap data", "pending", []
    matches = tcp.get("os_matches", [])
    if isinstance(matches, list) and matches and isinstance(matches[0], dict):
        best = matches[0]
        name = safe_text(best.get("name"), 100) or "Unclassified OS"
        score = str(best.get("accuracy") or "")
        os_name = "Nmap inferred: " + name
        if score.isdecimal() and int(score) <= 100:
            os_name += " (match score " + score + "%)"
        confidence = "inferred"
    else:
        os_name, confidence = "Unknown — no reliable OS match", "pending"
    ports = []
    for port in tcp.get("ports", [])[:30]:
        if not isinstance(port, dict):
            continue
        try:
            number = int(port.get("port"))
        except (TypeError, ValueError):
            continue
        if not 1 <= number <= 65535:
            continue
        service = port.get("service")
        if not isinstance(service, dict):
            service = {}
        ports.append(str(number) + "/tcp " + safe_text(service.get("name"), 40))
    return os_name, confidence, ports[:16]


def uid_for(mac):
    return "routerdhcp-" + hashlib.sha256(mac.encode("ascii")).hexdigest()[:20]


def dashboard(mac, rec, inventory, profiles):
    ip = rec["ip"]
    record = inventory.get(ip)
    if isinstance(record, dict) and clean_mac(record.get("mac")) == mac:
        vendor = safe_text(record.get("vendor"), 80) or "Unknown"
        online = ("Online at last LAN scan" if record.get("online")
                  else "Offline at last LAN scan")
    else:
        vendor, online = "Unknown", "Not correlated with current scan"
    name = safe_text(rec.get("hostname"), 80) or "Unnamed"
    os_name, confidence, ports = os_and_ports(mac, ip, profiles)
    timestamp = datetime.fromtimestamp(
        rec["last_seen_ns"] / 10**9, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary = "\n\n".join((
        "### Identity from router-01 dnsmasq",
        "**Hostname:** " + name,
        "**MAC:** " + mac,
        "**Last DHCP IP:** " + ip,
        "**Last DHCPACK:** " + timestamp,
        "**Manufacturer (discovery):** " + vendor,
        "**LAN scan:** " + online,
        "**Operating system:** " + os_name,
        "**OS evidence:** " + confidence,
        "**Observed TCP ports:** " + ("; ".join(ports) if ports else "Not available"),
        "DHCP does not prove the device is online. Nmap OS is an inference, not a confirmed fact."
    ))
    prom = {"type": "prometheus", "uid": "prometheus"}
    loki = {"type": "loki", "uid": "loki"}
    selector = '{ip="' + ip + '"}'
    return {
        "id": None, "uid": uid_for(mac),
        "title": "Router DHCP — " + name + " (" + ip + ")",
        "description": "Router-01 DHCP source and monitor-01 Nmap supporting evidence.",
        "tags": ["homelab", "router-01", "dhcp", "auto-device"],
        "editable": False, "schemaVersion": 41, "version": 1,
        "timezone": "browser", "refresh": "1m",
        "time": {"from": "now-24h", "to": "now"},
        "templating": {"list": []}, "annotations": {"list": []},
        "panels": [
            {"id": 1, "type": "text", "title": "Identity, OS and detected services",
             "gridPos": {"x": 0, "y": 0, "w": 24, "h": 9},
             "options": {"mode": "markdown", "content": summary}},
            {"id": 2, "type": "stat", "title": "LAN presence",
             "gridPos": {"x": 0, "y": 9, "w": 8, "h": 5},
             "datasource": prom,
             "targets": [{"refId": "A",
                          "expr": "max(homelab_network_host_up" + selector + ")",
                          "instant": True, "range": False}],
             "fieldConfig": {"defaults": {"min": 0, "max": 1}, "overrides": []},
             "options": {"reduceOptions": {"values": False,
                          "calcs": ["lastNotNull"], "fields": ""}}},
            {"id": 3, "type": "timeseries", "title": "LAN discovery history",
             "gridPos": {"x": 8, "y": 9, "w": 16, "h": 5},
             "datasource": prom,
             "targets": [{"refId": "A",
                          "expr": "homelab_network_host_up" + selector,
                          "instant": False, "range": True}],
             "fieldConfig": {"defaults": {"min": 0, "max": 1}, "overrides": []}},
            {"id": 4, "type": "logs", "title": "Router-01 DHCPACK history",
             "gridPos": {"x": 0, "y": 14, "w": 24, "h": 8},
             "datasource": loki,
             "targets": [{
                 "refId": "A",
                 "expr": '{host="router-01",service="dnsmasq"} |= "DHCPACK" |= "' + mac + '"',
                 "queryType": "range", "datasource": loki}],
             "options": {"showTime": True, "showLabels": False,
                         "wrapLogMessage": True}},
        ]
    }


def atomic_json(path, obj, *, apply, mode=0o644):
    payload = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    if path.is_symlink():
        raise ValueError("Symlink output refused")
    if path.exists():
        if not path.is_file():
            raise ValueError("Refusing non-file output")
        if path.read_text() == payload:
            return False
    if not apply:
        return True
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise ValueError("Output directory absent/unsafe")
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".router-dhcp-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            # Dashboard JSON is provisioner-readable; MAC state stays 0600.
            os.fchmod(out.fileno(), mode)
            out.write(payload)
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return True


def reconcile(events, inventory, profiles, state, output_dir, state_path,
              *, apply=False, max_new=None):
    updated, added = merge_events(state, events, max_new=max_new)
    if not updated["devices"]:
        raise ValueError("No authenticated router DHCPACK device records")
    writes = 0
    for mac, rec in sorted(updated["devices"].items()):
        filename = uid_for(mac) + ".json"
        if atomic_json(output_dir / filename,
                       dashboard(mac, rec, inventory, profiles), apply=apply):
            writes += 1
    state_write = atomic_json(state_path, updated, apply=apply, mode=0o600)
    return {"device_pages": len(updated["devices"]), "new_devices": added,
            "dashboard_writes": writes, "state_change": bool(state_write),
            "mode": "apply" if apply else "check", "no_deletions": True}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--loki", default="http://127.0.0.1:3100")
    parser.add_argument("--inventory", type=Path, default=Path(
        "/var/lib/homelab-network-hosts/inventory.json"))
    parser.add_argument("--profiles", type=Path, default=Path(
        "/var/lib/homelab-network-hosts/deep-profiles.json"))
    parser.add_argument("--state", type=Path, default=Path(
        "/var/lib/homelab-network-hosts/router-dhcp-device-pages.json"))
    parser.add_argument("--output-dir", type=Path, default=Path(
        "/opt/monitoring/grafana/provisioning/dashboards/router-dhcp-devices"))
    parser.add_argument("--max-new", type=int)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if args.max_new is not None and not 1 <= args.max_new <= MAX_DEVICES:
        parser.error("--max-new must be in the range 1..254")
    if args.loki != "http://127.0.0.1:3100":
        parser.error("Only local monitor-01 Loki is an approved source")
    inventory = read_json(args.inventory)
    profiles = read_json(args.profiles)
    if not isinstance(inventory, dict) or not isinstance(profiles, dict):
        raise ValueError("Unexpected inventory or profile format")
    lock = None
    if args.apply:
        lock_path = args.state.with_suffix(".lock")
        if lock_path.is_symlink() or not lock_path.parent.is_dir():
            raise ValueError("Unsafe state lock location")
        lock = os.open(str(lock_path),
                       os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        state = load_state(args.state)
        events = read_loki(args.loki, time.time_ns())
        print(json.dumps(reconcile(
            events, inventory, profiles, state, args.output_dir, args.state,
            apply=args.apply, max_new=args.max_new), sort_keys=True))
    finally:
        if lock is not None:
            os.close(lock)


if __name__ == "__main__":
    main()
