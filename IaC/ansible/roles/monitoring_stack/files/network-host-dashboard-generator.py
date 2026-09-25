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


def profile(template, key, metric):
    result = copy.deepcopy(template)
    result["id"] = None
    result["uid"] = uid_for(key)
    name = (metric.get("hostname") or metric.get("ip") or "").strip()[:85]
    if not name:
        raise ValueError("Device has no human-readable hostname or IP")
    result["title"] = "Homelab — %s" % name
    result["description"] = (
        "Automatically generated from MAC/IP evidence. Current identity, "
        "OS source, DNS hints and observed open ports refresh from Prometheus."
    )
    result["version"] = 1
    result["tags"] = sorted(set(
        result.get("tags", []) + ["generated-network-host"]))
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
            "hide": 0, "current": {
                "selected": True, "text": name, "value": name
            }
        })
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
    changed = 0
    for key, metric in sorted(cards.items()):
        body = json.dumps(
            profile(template, key, metric),
            indent=2, ensure_ascii=False) + "\n"
        if atomic_write(OUTPUT_DIR / (uid_for(key) + ".json"), body):
            changed += 1
    stale = 0
    for path in old_files:
        if path.name not in expected:
            path.unlink()
            stale += 1
    print("Generated %d MAC-linked Grafana dashboards; changed=%d stale=%d" %
          (len(cards), changed, stale))


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        print("Host dashboard generator: %s" % exc, file=sys.stderr)
        sys.exit(1)
