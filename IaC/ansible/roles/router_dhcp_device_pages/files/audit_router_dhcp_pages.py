#!/usr/bin/env python3
"""Read-only Grafana identity/provisioning guard for router DHCP device pages."""
import argparse
import base64
import hashlib
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

EXPECTED_16_HASH = "1ba5e96a3b2bc01aef7efe97d8ee8b11464baa8bb44572eae52b45d3f87abc13"
UID_RE = re.compile(r"routerdhcp-[0-9a-f]{20}\Z")
FOLDER_UID = "router-dhcp-devices"
DIR = Path("/opt/monitoring/grafana/provisioning/dashboards/router-dhcp-devices")


def credential():
    file = Path("/opt/monitoring/.env")
    if file.is_symlink() or not file.is_file():
        raise ValueError("Grafana credential source unavailable")
    settings = {}
    for line in file.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            settings[key.strip()] = value.strip()
    password = settings.get("GF_SECURITY_ADMIN_PASSWORD", "")
    if (password.startswith('"') and password.endswith('"')) or (
            password.startswith("'") and password.endswith("'")):
        password = password[1:-1]
    if not password:
        raise ValueError("Grafana admin credential not found")
    result = base64.b64encode(("admin:" + password).encode()).decode()
    del password
    return result


def get(path, auth):
    req = urllib.request.Request(
        "http://127.0.0.1:3000" + path,
        headers={"Authorization": "Basic " + auth,
                 "Accept": "application/json"}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=12) as res:
            return json.loads(res.read(4_000_000))
    except Exception:
        raise ValueError("Grafana API unavailable or unsupported") from None


def check(mode):
    auth = credential()
    data = get("/api/search?type=dash-db&limit=5000", auth)
    if not isinstance(data, list) or not 0 < len(data) < 5000:
        raise ValueError("Grafana dashboard search response invalid")
    found = {str(row.get("uid") or ""): row for row in data
             if isinstance(row, dict)}
    if len(found) != len(data) or "" in found:
        raise ValueError("Grafana dashboard UID collision or missing UID")
    pages = {u for u in found if UID_RE.fullmatch(u)}
    retained = set(found) - pages
    digest = hashlib.sha256("|".join(sorted(retained)).encode()).hexdigest()
    if len(retained) != 16 or digest != EXPECTED_16_HASH:
        raise ValueError("Protected Grafana dashboards changed")
    if not {"homelab-network-hosts", "homelab-router-dhcp"}.issubset(retained):
        raise ValueError("Protected network discovery/router dashboard absent")
    if mode == "before" and (len(data) != 16 or pages):
        raise ValueError("Pre-activation Grafana baseline not the original 16")
    if mode == "canary" and (len(data) != 17 or len(pages) != 1):
        raise ValueError("Canary did not create exactly one device dashboard")
    if mode == "enabled" and not 1 <= len(pages) <= 254:
        raise ValueError("Enabled router DHCP dashboard count invalid")
    if mode in ("canary", "enabled"):
        if DIR.is_symlink() or not DIR.is_dir():
            raise ValueError("Dedicated router DHCP dashboard directory unavailable")
        for uid in pages:
            detail = get("/api/dashboards/uid/" + uid, auth)
            meta = detail.get("meta") or {}
            if (detail.get("dashboard", {}).get("uid") != uid
                    or meta.get("provisioned") is not True
                    or meta.get("folderUid") != FOLDER_UID
                    or meta.get("provisionedExternalId") != uid + ".json"
                    or found[uid].get("folderUid") != FOLDER_UID):
                raise ValueError("Dashboard provenance mismatch")
            file = DIR / (uid + ".json")
            if file.is_symlink() or not file.is_file():
                raise ValueError("Provisioned router DHCP page source absent")
            if json.loads(file.read_text()).get("uid") != uid:
                raise ValueError("Provisioned JSON and live UID disagree")
    return {"mode": mode, "protected_dashboards": 16,
            "router_dhcp_device_dashboards": len(pages),
            "total_dashboards": len(found),
            "protected_uid_fingerprint_verified": True,
            "read_only": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("before", "canary", "enabled"),
                        required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.mode), sort_keys=True))


if __name__ == "__main__":
    main()
