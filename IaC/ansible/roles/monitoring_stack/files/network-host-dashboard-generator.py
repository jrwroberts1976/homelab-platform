#!/usr/bin/env python3
"""Generate one native Grafana dashboard per retained device MAC.

Uses the existing MAC-keyed Prometheus card metric, not a new LAN scan.
Generated dashboard UIDs remain stable across IP and hostname changes.
"""
import copy
import hashlib
import ipaddress
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

PROMETHEUS = "http://127.0.0.1:9090/api/v1/query"
TEMPLATE = Path("/etc/homelab/network-host-template.json")
OUTPUT_DIR = Path("/opt/monitoring/grafana/provisioning/dashboards/network-hosts")
LAN = ipaddress.ip_network("192.168.2.0/24")
MAC_RE = re.compile(r"^mac:(?:[0-9a-f]{2}:){5}[0-9a-f]{2}$")
UID_RE = re.compile(r"^net-host-[0-9a-f]{12}$")


def valid_key(key):
    if MAC_RE.fullmatch(key):
        return True
    if not key.startswith("ip:"):
        return False
    try:
        return ipaddress.ip_address(key[3:]) in LAN
    except ValueError:
        return False


def uid_for(key):
    return "net-host-" + hashlib.sha256(
        key.encode("utf-8")).hexdigest()[:12]


def clean_hostname(value):
    """Return the short, human-facing hostname used in Grafana titles."""
    hostname = str(value or "").strip()
    suffix = ".jameshouse"
    if hostname.casefold().endswith(suffix):
        hostname = hostname[:-len(suffix)]
    return hostname


def publishable_card(metric):
    """Hide unresolved IP-only records from the generated host directory."""
    hostname = clean_hostname(metric.get("hostname"))
    ip = str(metric.get("ip") or "").strip()
    kind = str(metric.get("kind") or "").strip()
    return bool((hostname and hostname != ip) or kind)


def query_cards():
    expr = 'homelab_network_device_card_info{target_name="monitor-01"}'
    with urlopen(PROMETHEUS + "?" + urlencode({"query": expr}),
                 timeout=15) as response:
        result = json.load(response)
    if result.get("status") != "success":
        raise ValueError("Prometheus inventory query failed")
    cards = {}
    for series in result.get("data", {}).get("result", []):
        metric = series.get("metric", {})
        key = metric.get("device_key", "")
        uid = metric.get("dashboard_uid", "")
        if not valid_key(key) or not UID_RE.fullmatch(uid):
            continue
        if uid != uid_for(key):
            raise ValueError("Device UID does not match the MAC-derived identity")
        if key in cards:
            raise ValueError("Duplicate device key " + key)
        cards[key] = metric
    if not 10 <= len(cards) <= 254:
        raise ValueError(
            "Suspicious dashboard count %d; preserving previous files" %
            len(cards))
    return cards



# A panel is included only if its underlying data was recorded in the same
# 24-hour window as the default Grafana time range. A legitimate zero (for
# example 0 security updates) still counts as data.
AVAILABILITY_QUERIES = {
    "cpu": 'node_cpu_seconds_total{job="node-exporter",mode="idle"}',
    "memory": 'node_memory_MemAvailable_bytes{job="node-exporter"}',
    "memory_total": 'node_memory_MemTotal_bytes{job="node-exporter"}',
    "network": 'node_network_receive_bytes_total{job="node-exporter",device!~"lo|veth.*|docker.*|br-.*|virbr.*|cni.*|flannel.*|tun.*|tap.*"}',
    "filesystem": 'node_filesystem_avail_bytes{job="node-exporter",fstype!~"tmpfs|devtmpfs|overlay|squashfs"}',
    "filesystem_size": 'node_filesystem_size_bytes{job="node-exporter",fstype!~"tmpfs|devtmpfs|overlay|squashfs"}',
    "updates": 'homelab_updates_available',
    "security_updates": 'homelab_security_updates_available',
    "disk": 'node_disk_read_bytes_total{job="node-exporter",device!~"loop.*|ram.*"}',
    "load": 'node_load1{job="node-exporter"}',
    "os": 'node_os_info',
}


def query_vector(expr):
    """Run an instant PromQL query without mutating Prometheus."""
    with urlopen(PROMETHEUS + "?" + urlencode({"query": expr}),
                 timeout=20) as response:
        payload = json.load(response)
    if payload.get("status") != "success":
        raise ValueError("Prometheus did not return metric availability")
    return payload.get("data", {}).get("result", [])


def collect_availability():
    """Batch data presence by hostname, avoiding queries for every device."""
    available = {name: set() for name in AVAILABILITY_QUERIES}
    for name, selector in AVAILABILITY_QUERIES.items():
        expr = "count by(target_name) (present_over_time(%s[24h]))" % selector
        for series in query_vector(expr):
            hostname = series.get("metric", {}).get("target_name")
            if hostname and float(series.get("value", [0, "0"])[1]) > 0:
                available[name].add(hostname)
    port_keys = {
        s.get("metric", {}).get("device_key", "")
        for s in query_vector(
            'homelab_network_device_card_port_info{target_name="monitor-01"}')
    }
    last_seen_keys = {
        s.get("metric", {}).get("device_key", "")
        for s in query_vector(
            'homelab_network_device_card_last_seen_seconds{target_name="monitor-01"}')
    }
    presence_keys = {
        s.get("metric", {}).get("device_key", "")
        for s in query_vector(
            'homelab_network_device_card_online{target_name="monitor-01"}')
    }
    ai_change_keys = {
        s.get("metric", {}).get("device_key", "")
        for s in query_vector(
            'homelab_network_device_ai_assessment_change_info'
            '{target_name="monitor-01"}')
    }
    zabbix_os_last_seen_keys = {
        s.get("metric", {}).get("device_key", "")
        for s in query_vector(
            'homelab_network_device_zabbix_os_last_seen_seconds'
            '{target_name="monitor-01"}')
    }
    return (
        available,
        port_keys,
        last_seen_keys,
        presence_keys,
        ai_change_keys,
        zabbix_os_last_seen_keys,
    )


def os_requires_fingerprint(metric, live_os_available):
    """Identify only hosts whose OS is not already known from stronger data.

    A documented *specific* OS or live OS-release information is sufficient
    for this dashboard; Nmap remains an optional clue for unknown/inferred
    hosts and for generic inventory entries such as 'Linux (IaC-managed)'.
    'Documented' alone is not proof that a distribution/version is known.
    """
    if live_os_available:
        return False
    if metric.get("os_evidence") == "authoritative":
        return False
    if metric.get("os_evidence") != "documented":
        return True
    documented = (metric.get("os") or "").strip().casefold()
    return documented in ("", "unknown", "linux", "linux (iac-managed)")


def select_panel_ids(key, metric, availability):
    metrics, port_keys, last_seen_keys, presence_keys = availability[:4]
    ai_change_keys = availability[4] if len(availability) > 4 else set()
    zabbix_os_last_seen_keys = (
        availability[5] if len(availability) > 5 else set()
    )
    host = metric.get("hostname", "")
    present = lambda name: host in metrics[name]
    # Keep a zero-valued update/security metric if it was observed.
    selected = {14}  # Host identity and OS are present for every inventory item.
    if present("cpu"):
        selected.update((1, 5))
    if present("memory") and present("memory_total"):
        selected.update((2, 6))
    if present("updates"):
        selected.add(3)
    if present("security_updates"):
        selected.add(4)
    if present("network"):
        selected.add(7)
    if present("filesystem") and present("filesystem_size"):
        selected.add(8)
    if key in presence_keys and metric.get("status") in ("Online", "Offline"):
        selected.update((9, 17))
    if key in last_seen_keys:
        selected.add(10)
    if key in port_keys:
        selected.update((11, 15))
    if metric.get("dns_hint", "").strip():
        selected.add(16)
    if (metric.get("nmap_name", "").strip()
            and os_requires_fingerprint(metric, present("os"))):
        selected.add(22)  # Only when OS identification needs investigation.
    if metric.get("ai_summary", "").strip():
        selected.add(23)  # Advisory AI assessment; deterministic facts remain authoritative.
    if key in ai_change_keys:
        selected.add(25)  # Bounded structured AI assessment changes only.
    if key in zabbix_os_last_seen_keys:
        selected.add(26)  # Timestamp exists only after a Zabbix OS observation.
    if metric.get("greenbone_findings", "").strip():
        selected.add(24)  # Deterministic actionable Greenbone findings only.
    if present("disk"):
        selected.add(18)
    if present("load"):
        selected.add(19)
    if present("os"):
        selected.add(20)
    # Panel 12 (Linux exporter available), text 13 and optional log panel 21
    # add clutter or cannot be proven to contain real data; omit them.
    return selected


def compact_panels(template_panels, selected):
    """Remove absent panels and reflow without giant holes or empty rows."""
    panels = {p["id"]: copy.deepcopy(p) for p in template_panels}
    missing = selected - panels.keys()
    if missing:
        raise ValueError("Host template missing panels: %r" % sorted(missing))
    chosen = []
    top_order = (1, 2, 3, 4, 9, 10, 11)
    current_y = 0
    stats = [panels[i] for i in top_order if i in selected]
    for start in range(0, len(stats), 4):
        row = stats[start:start + 4]
        width = 24 // len(row)
        for index, panel in enumerate(row):
            panel["gridPos"] = {
                "x": index * width,
                "y": current_y,
                "w": 24 - index * width if index == len(row) - 1 else width,
                "h": 4,
            }
            chosen.append(panel)
        current_y += 4
    # Grafana-like charts first, then actionable inventory/evidence tables.
    def add_row(ids, height):
        nonlocal current_y
        row = [panels[i] for i in ids if i in selected]
        if not row:
            return
        width = 24 // len(row)
        for index, panel in enumerate(row):
            panel["gridPos"] = {
                "x": index * width, "y": current_y,
                "w": 24 - index * width if index == len(row) - 1 else width,
                "h": height,
            }
            chosen.append(panel)
        current_y += height

    add_row((5, 6), 8)
    add_row((7, 8), 8)
    add_row((14,), 6)
    add_row((22,), 8)
    add_row((23,), 8)
    add_row((25,), 8)
    add_row((24,), 8)
    add_row((15,), 7)
    add_row((16,), 6)
    add_row((17,), 7)
    add_row((18, 19), 8)
    add_row((20,), 6)
    if len(chosen) != len(selected):
        raise ValueError("Internal panel layout lost requested data panels")
    return chosen


def profile(template, key, metric, availability=None):
    result = copy.deepcopy(template)
    result["id"] = None
    result["uid"] = uid_for(key)
    hostname = clean_hostname(metric.get("hostname"))
    ip = (metric.get("ip") or "").strip()
    kind = (metric.get("kind") or "").strip()

    # For unidentified devices the exporter intentionally falls back to using
    # the IP address as the hostname. Once correlated evidence supplies a useful
    # device type, prefer that friendly identity in the generated dashboard
    # title while retaining the IP for disambiguation.
    if kind and (not hostname or hostname == ip):
        name = ("%s (%s)" % (kind, ip)).strip()[:85]
    else:
        name = (hostname or ip or kind).strip()[:85]

    if not name:
        raise ValueError("Device has no human-readable hostname, IP or type")
    result["title"] = "Homelab — %s" % name
    result["description"] = (
        "Automatically generated from MAC/IP evidence. Current identity, "
        "OS source, DNS hints, observed ports and correlated saved Nmap "
        "fingerprints refresh from Prometheus when the OS is unresolved; "
        "documented specific or live OS facts take precedence."
    )
    result["version"] = 2
    if availability is not None:
        result["panels"] = compact_panels(
            result["panels"], select_panel_ids(key, metric, availability))
    # Keep generated dashboards easy to browse: one functional selector tag
    # plus one broad homelab grouping tag. The old five generic tags repeated
    # beneath every dashboard and added visual noise without improving lookup.
    result["tags"] = ["generated-network-host", "homelab"]
    variables = result.get("templating", {}).get("list", [])
    device = next((v for v in variables if v.get("name") == "device"), None)
    if device is None:
        raise ValueError("Profile template lacks device variable")
    device.clear()
    device.update({
        "name": "device", "label": "Internal identity",
        "type": "constant", "query": key,
        "hide": 2, "current": {
            "selected": True, "text": key, "value": key
        }
    })
    # The user's header and variable display the hostname, never a MAC.
    host = next((v for v in variables if v.get("name") == "host"), None)
    if host is not None:
        host.clear()
        host.update({
            "name": "host", "label": "Host",
            "type": "constant", "query": name,
            "hide": 2, "current": {
                "selected": True, "text": name, "value": name
            }
        })
    # Native Grafana dashboard-link dropdown navigates to the *actual*
    # per-host JSON. A single variable-driven dashboard cannot reflow its
    # panels when the selected host changes. All generated pages have the
    # generated-network-host tag, so the selector displays friendly titles.
    result["links"] = [
        {
            "title": "Choose host",
            "type": "dashboards",
            "tags": ["generated-network-host"],
            "asDropdown": True,
            "includeVars": False,
            "keepTime": True,
            "targetBlank": False,
        },
        {
            "title": "All Hosts",
            "type": "link",
            "url": "/d/homelab-network-host-tiles",
            "includeVars": False,
            "keepTime": True,
            "targetBlank": False,
        },
    ]
    return result


def atomic_write(path, text):
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    fd, tmp = tempfile.mkstemp(
        prefix=".network-host-", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return True


def run():
    cards = query_cards()
    cards = {
        key: metric
        for key, metric in cards.items()
        if publishable_card(metric)
    }
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    if template.get("uid") != "homelab-mac-device-detail":
        raise ValueError("Unexpected Grafana profile template")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True, mode=0o755)
    expected = {
        uid_for(key) + ".json"
        for key in cards
    }
    old_files = list(OUTPUT_DIR.glob("net-host-*.json"))
    # A sudden large drop in the metrics is a source failure, not permission
    # to delete all per-host dashboards.
    if old_files and len(cards) < len(old_files) * 0.80:
        raise ValueError("Inventory dropped sharply; retaining last good dashboards")
    availability = collect_availability()
    changed = 0
    for key, metric in sorted(cards.items()):
        body = json.dumps(
            profile(template, key, metric, availability),
            indent=2, ensure_ascii=False) + "\n"
        if atomic_write(OUTPUT_DIR / (uid_for(key) + ".json"), body):
            changed += 1
    stale = 0
    for path in old_files:
        if path.name not in expected:
            path.unlink()
            stale += 1
    print("Generated %d data-only host dashboards; changed=%d stale=%d" %
          (len(cards), changed, stale))


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        print("Host dashboard generator: %s" % exc, file=sys.stderr)
        sys.exit(1)
