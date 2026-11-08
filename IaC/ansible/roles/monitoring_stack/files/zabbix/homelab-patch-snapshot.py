#!/usr/bin/env python3
"""Read-only, low-write snapshot of cached APT patch metadata for Zabbix."""
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone

def main():
    now = datetime.now(timezone.utc)
    result = {
        "schema_version": 1,
        "collected_at": now.isoformat(),
        "source": "cached_apt_no_refresh",
        "pending_updates_cached": None,
        "apt_index_latest_utc": None,
        "apt_index_age_hours": None,
        "reboot_required_flag": Path("/run/reboot-required").exists(),
        "security_updates": None,
        "last_verified_patch_utc": None,
        "error": None,
    }
    try:
        proc = subprocess.run(
            ["/usr/bin/apt", "list", "--upgradable"],
            capture_output=True, text=True, timeout=30,
            env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"},
        )
        if proc.returncode != 0:
            raise RuntimeError("cached apt list returned nonzero status")
        rows = [s for s in proc.stdout.splitlines()
                if s.strip() and not s.startswith("Listing")]
        if not all("/" in s and "[upgradable from:" in s for s in rows):
            raise RuntimeError("unrecognised apt list output")
        result["pending_updates_cached"] = len(rows)
        root = Path("/var/lib/apt/lists")
        files = [p for p in root.iterdir()
                 if p.is_file() and (p.name.endswith("_Packages") or "_Packages." in p.name)] if root.exists() else []
        if files:
            latest = max(p.stat().st_mtime for p in files)
            result["apt_index_latest_utc"] = datetime.fromtimestamp(latest, timezone.utc).isoformat()
            result["apt_index_age_hours"] = round(max(0, now.timestamp() - latest) / 3600, 1)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        result["error"] = str(exc)[:180]
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))

if __name__ == "__main__":
    main()
