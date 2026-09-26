#!/usr/bin/env python3
"""Publish *existing* MAC-keyed Nmap OS evidence; never initiate a scan.

Reads root-only deep-profiles.json on Proxmox-2. Exports a bounded, minimally
identified metric via the existing node-exporter textfile collector.
"""
import ipaddress
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

STATE = Path("/var/lib/homelab-network-hosts/deep-profiles.json")
OUTPUT = Path("/var/lib/prometheus/node-exporter/homelab_network_os_fingerprints.prom")
LAN = ipaddress.ip_network("192.168.2.0/24")
MAC_RE = re.compile(r"^(?:[0-9a-f]{2}:){5}[0-9a-f]{2}$")


def label(value, limit=128):
    return (str(value or "")[:limit].replace("\\", "\\\\")
            .replace('"', '\\"').replace("\n", " ").replace("\r", " "))


def labels(fields):
    return ",".join('%s="%s"' % (key, label(value)) for key, value in fields.items())


def accuracy(value):
    """Nmap-reported score, not a statistical probability."""
    try:
        result = int(float(value))
    except (ValueError, TypeError):
        return -1
    return result if 0 <= result <= 100 else -1


def evidence(state):
    if not isinstance(state, dict) or not isinstance(state.get("profiles"), dict):
        raise ValueError("Invalid deep-profile JSON; preserve previous published evidence")
    results = []
    for mac, record in sorted(state["profiles"].items()):
        mac = str(mac).lower().strip()
        if not MAC_RE.fullmatch(mac) or not isinstance(record, dict):
            continue
        if record.get("status") not in ("complete", "partial"):
            continue
        try:
            ip = str(ipaddress.ip_address(record.get("profiled_ip", "")))
            if ipaddress.ip_address(ip) not in LAN:
                continue
        except ValueError:
            continue
        profile = record.get("profile") or {}
        tcp = profile.get("tcp") or {}
        if not isinstance(tcp, dict):
            continue
        matches = tcp.get("os_matches") or []
        valid = [(accuracy(m.get("accuracy")), m)
                 for m in matches if isinstance(m, dict) and m.get("name")]
        valid = [(score, match) for score, match in valid if score >= 0]
        if not valid:
            continue
        score, match = max(valid, key=lambda item: item[0])
        try:
            scanned = int(profile.get("tcp_scanned_at") or 0)
            # Skip missing, pre-2020, or future dates instead of inventing recency.
            if not 1577836800 <= scanned <= int(datetime.now(timezone.utc).timestamp()) + 300:
                continue
            observed = datetime.fromtimestamp(scanned, timezone.utc).strftime(
                "%Y-%m-%d %H:%M UTC")
        except (TypeError, ValueError, OverflowError):
            continue
        classes = match.get("classes") or []
        primary = next((c for c in classes if isinstance(c, dict)), {})
        cpes = primary.get("cpe") or []
        first_cpe = next((str(c) for c in cpes if c), "")
        services = []
        for port in tcp.get("ports") or []:
            if not isinstance(port, dict) or port.get("state") != "open":
                continue
            svc = port.get("service") or {}
            if not isinstance(svc, dict):
                svc = {}
            try:
                number = int(port.get("port"))
            except (ValueError, TypeError):
                continue
            if not 1 <= number <= 65535:
                continue
            detail = " ".join(str(svc.get(key) or "").strip()[:28]
                              for key in ("name", "product", "version")).strip()
            services.append("%d/%s %s" % (
                number, str(port.get("protocol") or "tcp")[:4], detail))
        services = sorted(services)[:5]
        results.append({
            "mac": mac,
            "profiled_ip": ip,
            "nmap_name": str(match["name"])[:120],
            "nmap_accuracy": str(score) + "%",
            "nmap_family": str(primary.get("os_family") or "")[:80],
            "nmap_generation": str(primary.get("os_generation") or "")[:40],
            "nmap_vendor": str(primary.get("vendor") or "")[:80],
            "nmap_device_type": str(primary.get("type") or "")[:60],
            "nmap_cpe": first_cpe[:120],
            "nmap_scanned_at": observed,
            "nmap_services": "; ".join(services)[:360],
            "nmap_scan_status": str(record["status"]),
            "scanned": scanned,
        })
    return results


def render(results):
    lines = [
        "# HELP homelab_network_host_os_fingerprint_info Existing Nmap OS evidence keyed by MAC and scanned IP; a match is an inference, never proof.",
        "# TYPE homelab_network_host_os_fingerprint_info gauge",
        "# HELP homelab_network_host_os_fingerprint_scan_timestamp_seconds Timestamp of the recorded TCP fingerprint scan.",
        "# TYPE homelab_network_host_os_fingerprint_scan_timestamp_seconds gauge",
    ]
    for rec in results:
        fields = {k: v for k, v in rec.items() if k != "scanned"}
        # The inventory exporter will match BOTH MAC and observed IP.
        lines.append("homelab_network_host_os_fingerprint_info{" + labels(fields) + "} 1")
        lines.append(
            "homelab_network_host_os_fingerprint_scan_timestamp_seconds{" +
            labels({k: rec[k] for k in ("mac", "profiled_ip")}) +
            "} " + str(rec["scanned"]))
    return "\n".join(lines) + "\n"


def atomic_publish(text):
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".nmap-os-", suffix=".prom",
                                 dir=str(OUTPUT.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(name, 0o644)
        os.replace(name, OUTPUT)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main():
    raw = json.loads(STATE.read_text(encoding="utf-8"))
    results = evidence(raw)
    atomic_publish(render(results))
    print("Exported %d *existing* Nmap OS fingerprints; scans_started=0" % len(results))


if __name__ == "__main__":
    main()
