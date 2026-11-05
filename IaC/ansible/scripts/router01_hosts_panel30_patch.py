#!/usr/bin/env python3
"""Scoped patch of Grafana Homelab Hosts panel 30 only. No API or scanner calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

LIVE = Path("/opt/monitoring/grafana/provisioning/dashboards/production/homelab-linux-estate.json")
STAGE = Path("/var/backups/homelab-network-enrichment/independent-20261105")
BACKUP = STAGE / "grafana-hosts-before-panel30.json"
DEPLOYED_HASH = STAGE / "grafana-hosts-after-panel30.sha256"
OLD = 'max by (ip, port, protocol, service, product, version) (homelab_network_host_enrichment_port_info * on(ip) group_left(hostname) (homelab_network_device_card_info{hostname="$host"} == 1))'
NEW = 'max by (ip, port, protocol, service, product, version) (homelab_network_host_enrichment_port_info{target_name="monitor-01"} * on(ip) group_left(hostname) (homelab_network_host_info{target_name="monitor-01",hostname=~"^${host:regex}(\\\\..*)?$"} == 1))'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(data):
    return json.loads(data.decode("utf-8"))


def panel(dashboard, pid):
    matches = [p for p in dashboard.get("panels", []) if p.get("id") == pid]
    if len(matches) != 1 or len(matches[0].get("targets", [])) != 1:
        raise ValueError(f"Expected exactly one panel {pid} with one target")
    return matches[0]


def inspect(dashboard):
    if dashboard.get("uid") != "homelab-linux-estate":
        raise ValueError("Unexpected Grafana dashboard")
    os_expr = panel(dashboard, 29)["targets"][0]["expr"]
    if 'node_os_info{job="router-node-exporter"' not in os_expr:
        raise ValueError("Deployed panel 29 OS fallback absent; refuse to modify")
    return os_expr, panel(dashboard, 30)["targets"][0]["expr"]


def atomic_write(path, content, original_stat):
    fd, name = tempfile.mkstemp(prefix=".homelab-hosts-panel30-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(name, original_stat.st_mode & 0o777)
        os.chown(name, original_stat.st_uid, original_stat.st_gid)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["preflight", "apply", "verify", "rollback"])
    args = parser.parse_args()

    if not STAGE.is_dir() or not LIVE.is_file():
        raise SystemExit("Missing protected staging directory or live dashboard")
    if STAGE.stat().st_uid != 0 or (STAGE.stat().st_mode & 0o777) != 0o700:
        raise SystemExit("Unexpected staging directory owner/mode")

    original = LIVE.read_bytes()
    dashboard = load(original)
    _, current = inspect(dashboard)
    original_stat = LIVE.stat()

    if args.mode in ("preflight", "apply"):
        if current != OLD:
            raise SystemExit("Panel 30 differs from expected original; no change")
        if BACKUP.exists() or DEPLOYED_HASH.exists():
            raise SystemExit("Prior panel-30 deployment evidence exists; refuse overwrite")
        if args.mode == "preflight":
            print("PASS: panel29 fallback intact, panel30 expected legacy query, no old backup")
            return
        updated = load(original)
        panel(updated, 30)["targets"][0]["expr"] = NEW
        payload = (json.dumps(updated, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        # Confirm no other dashboard object changes (comparison ignores serialization).
        comparison = load(payload)
        panel(comparison, 30)["targets"][0]["expr"] = OLD
        if comparison != dashboard:
            raise SystemExit("Scope violation: more than panel30 changed")
        BACKUP.write_bytes(original)
        os.chmod(BACKUP, 0o600)
        atomic_write(LIVE, payload, original_stat)
        DEPLOYED_HASH.write_text(digest(payload) + "\n")
        os.chmod(DEPLOYED_HASH, 0o600)
        print("APPLIED: panel 30 only, backup saved, panel 29 preserved")
        return

    if not BACKUP.is_file() or not DEPLOYED_HASH.is_file():
        raise SystemExit("Missing original backup or deployment hash")
    deployed_hash = DEPLOYED_HASH.read_text().strip()
    if digest(original) != deployed_hash or current != NEW:
        raise SystemExit("Dashboard changed since controlled deployment; refuse overwrite")

    backup = BACKUP.read_bytes()
    backed_dashboard = load(backup)
    backup_os, backup_ports = inspect(backed_dashboard)
    if backup_ports != OLD or backup_os != panel(dashboard, 29)["targets"][0]["expr"]:
        raise SystemExit("Backup is invalid or panel29 changed")
    if args.mode == "verify":
        print("PASS: deployed panel30 query, protected backup, panel29 unchanged")
        return
    # Roll back only when live bytes still exactly match this deployment.
    atomic_write(LIVE, backup, original_stat)
    print("ROLLED BACK: exact original dashboard restored; retained rollback evidence")


if __name__ == "__main__":
    main()
