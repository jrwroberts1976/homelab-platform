#!/usr/bin/env python3
"""Safely refresh an existing protected Proxmox guest-MAC snapshot.

Uses the previously verified, read-only cluster API publisher (strict TLS
with the privately installed PVE cluster CA) and the protected snapshot
identity validator. Never starts Nmap, edits LAN inventory, or starts timers.
On an API/validation failure, the existing snapshot is retained byte-for-byte.
The old snapshot is backed up BEFORE an atomic same-directory replacement.
No raw MAC, hostname, VMID, API token or JSON payload is printed.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import runpy
import ssl
import stat
import tempfile
import time

PUBLISHER = Path("/usr/local/sbin/homelab-proxmox-guest-mac-snapshot")
READER_DIR = "/usr/local/lib/homelab-network-hosts"
SNAPSHOT = Path("/var/lib/homelab-network-hosts/proxmox-guests.json")
INVENTORY = Path("/var/lib/homelab-network-hosts/inventory.json")
BACKUP_DIR = Path("/var/backups/homelab-network-migration/proxmox-guest-snapshots")
STALE_RECOVERY_SECONDS = 365 * 24 * 3600


def require_regular(path, owner_uid=0, mode=0o600):
    meta = Path(path).lstat()   # Never follow a symlink.
    if (not stat.S_ISREG(meta.st_mode)
            or meta.st_uid != owner_uid
            or stat.S_IMODE(meta.st_mode) != mode):
        raise ValueError("Protected guest snapshot/credential metadata is invalid")
    return meta


def read_state(path, inventory, now, owner_uid=0):
    import sys
    if READER_DIR not in sys.path:
        sys.path.insert(0, READER_DIR)
    from proxmox_guest_identity import load_snapshot
    return load_snapshot(
        path, inventory,
        max_age_seconds=STALE_RECOVERY_SECONDS,
        now=now,
        owner_uid=owner_uid,
    )


def compare_transition(old, new, inventory, now, owner_uid=0):
    """Validate both snapshots and reject large, unexplained visibility drops."""
    old_ids, old_counts = read_state(old, inventory, now, owner_uid)
    new_ids, new_counts = read_state(new, inventory, now, owner_uid)
    if new_counts["matched_guest_macs"] < 1:
        raise ValueError("Refusing a refresh with no saved LAN MAC overlap")
    # One guest being shut down is allowed; large API visibility changes
    # require manual review before we replace the known-good snapshot.
    if len(new_ids) * 4 < len(old_ids) * 3:
        raise ValueError("Large Proxmox guest visibility drop: old state retained")
    return {
        "previous_guest_macs": len(old_ids),
        "refreshed_guest_macs": len(new_ids),
        "matched_lan_macs": new_counts["matched_guest_macs"],
        "unmatched_lan_macs": new_counts["unmatched_guest_macs"],
        "previous_snapshot_age_seconds": old_counts["snapshot_age_seconds"],
    }


def backup_previous(path, backup_dir, raw, owner_uid=0):
    original_sha = hashlib.sha256(raw).hexdigest()
    backup = backup_dir / ("proxmox-guests." + original_sha + ".json")
    try:
        fd = os.open(
            backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
        )
    except FileExistsError:
        require_regular(backup, owner_uid)
        if hashlib.sha256(backup.read_bytes()).hexdigest() != original_sha:
            raise ValueError("Conflicting snapshot backup; no refresh performed")
        return backup, original_sha
    try:
        with os.fdopen(fd, "wb") as handle:
            os.fchmod(handle.fileno(), 0o600)
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.fsync(os.open(str(backup_dir), os.O_RDONLY | os.O_DIRECTORY))
    except BaseException:
        # Retain incomplete backup for investigation rather than overwrite it.
        raise
    return backup, original_sha


def refresh(path, inventory, backup_dir, candidate, *, now=None, owner_uid=0):
    """Testable, single-writer backup-first atomic replacement transaction."""
    now = int(time.time()) if now is None else now
    if (not backup_dir.is_dir()
            or backup_dir.is_symlink()
            or backup_dir.stat().st_uid != owner_uid
            or stat.S_IMODE(backup_dir.stat().st_mode) != 0o700):
        raise ValueError("Protected guest snapshot backup directory is unsafe")
    if not path.parent.is_dir():
        raise ValueError("Protected guest snapshot state directory is missing")

    lock = backup_dir / ".refresh.lock"
    fd = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "r+b") as lockfile:
            os.fchmod(lockfile.fileno(), 0o600)
            fcntl.flock(lockfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            require_regular(path, owner_uid)
            old_raw = path.read_bytes()
            old_sha = hashlib.sha256(old_raw).hexdigest()

            tmp_fd, tmp_path = tempfile.mkstemp(
                prefix=".proxmox-guests-refresh.", dir=str(path.parent),
            )
            tmp = Path(tmp_path)
            try:
                with os.fdopen(tmp_fd, "w", encoding="utf-8") as handle:
                    os.fchmod(handle.fileno(), 0o600)
                    json.dump(candidate, handle, sort_keys=True, indent=2)
                    handle.write("\n")
                    handle.flush()
                    os.fsync(handle.fileno())

                counts = compare_transition(
                    path, tmp, inventory, now, owner_uid,
                )
                # Recheck old state: another uncoordinated writer means stop.
                require_regular(path, owner_uid)
                if hashlib.sha256(path.read_bytes()).hexdigest() != old_sha:
                    raise ValueError("Original guest snapshot changed during refresh")
                backup, backed_up_sha = backup_previous(
                    path, backup_dir, old_raw, owner_uid,
                )
                if backed_up_sha != old_sha:
                    raise ValueError("Prior guest snapshot backup mismatch")
                os.replace(tmp, path)   # Atomic, same-directory replacement.
                directory_fd = os.open(
                    str(path.parent), os.O_RDONLY | os.O_DIRECTORY,
                )
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
            finally:
                tmp.unlink(missing_ok=True)
    except BlockingIOError as exc:
        raise RuntimeError("Another guest snapshot refresh is in progress") from exc

    return {
        **counts,
        "backup_verified": True,
        "snapshot_mode": "0600",
        "snapshot_updated": True,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def collect_candidate():
    import sys
    if READER_DIR not in sys.path:
        sys.path.insert(0, READER_DIR)
    # Existing publisher contains the previously deployed and tested
    # strict-TLS API and guest-NIC parser. It is root-owned and immutable.
    require_regular(PUBLISHER, owner_uid=0, mode=0o750)
    module = runpy.run_path(str(PUBLISHER), run_name="pve_publisher")
    token_id = os.environ.get("PVE_TOKEN_ID", "")
    token_secret = os.environ.get("PVE_TOKEN_SECRET", "")
    if not token_id or not token_secret:
        raise ValueError("Protected on-host API token is unavailable")
    context = ssl.create_default_context(cafile=module["CA_PATH"])
    auth = f"PVEAPIToken={token_id}={token_secret}"
    fetch = lambda node, endpoint: module["fetch_api"](
        node, endpoint, auth, context,
    )
    return module["collect"](
        fetch, module["inspect_inventory"](INVENTORY),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if os.geteuid() != 0:
        raise SystemExit("Guest refresh requires root to access the token")
    os.umask(0o077)
    require_regular(SNAPSHOT)
    if not BACKUP_DIR.is_dir():
        raise ValueError("The protected backup directory must already exist")
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    if not isinstance(inventory, dict):
        raise ValueError("Saved LAN inventory is invalid")

    candidate, api_summary = collect_candidate()
    if args.check:
        previous_ids, previous_counts = read_state(
            SNAPSHOT, inventory, int(time.time()),
        )
        # Check candidate without any disk mutation by comparing its
        # provenance, type and overlapping MACs in memory.
        new_guests = candidate.get("guests_by_mac")
        if not isinstance(new_guests, dict) or len(new_guests) < 2:
            raise ValueError("Read-only API returned no usable guest identities")
        if len(new_guests) * 4 < len(previous_ids) * 3:
            raise ValueError("Large API visibility drop in dry-run")
        print(json.dumps({
            "event": "proxmox_guest_refresh_preflight",
            "strict_tls": True,
            "previous_guest_macs": len(previous_ids),
            "candidate_guest_macs": len(new_guests),
            "candidate_matched_lan_macs": api_summary[
                "matches_staged_mac_inventory"
            ],
            "previous_snapshot_age_seconds": previous_counts[
                "snapshot_age_seconds"
            ],
            "snapshot_updated": False,
        }, sort_keys=True))
        return

    result = refresh(SNAPSHOT, inventory, BACKUP_DIR, candidate)
    result["event"] = "proxmox_guest_snapshot_refreshed"
    result["strict_tls"] = True
    # Do not reveal raw backups or identity labels in output.
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
