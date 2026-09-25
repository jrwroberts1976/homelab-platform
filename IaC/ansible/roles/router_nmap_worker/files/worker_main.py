"""Protected entry point for the router-triggered Nmap worker."""

import json
import os
import socket
import stat
import subprocess
from pathlib import Path

from profile_cycle import run_profile_once
from notification_delivery import deliver_next_notification

CONFIG = Path("/etc/homelab-router-nmap-worker.json")


def main():
    if os.geteuid() != 0:
        raise SystemExit("REFUSED: root privileges required")

    hostname = socket.gethostname().split(".")[0]
    if hostname != "monitor-01":
        raise SystemExit("REFUSED: incorrect deployment host")

    try:
        info = CONFIG.lstat()
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("Configuration must be a regular file")
        if info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o600:
            raise ValueError("Configuration must be root-owned, mode 0600")
        config = json.loads(CONFIG.read_text())
    except (OSError, ValueError) as exc:
        raise SystemExit(f"REFUSED: invalid configuration: {exc}")

    if config.get("allow_live_scans") is not True:
        raise SystemExit("REFUSED: live scanning not approved")
    if config.get("expected_hostname") != hostname:
        raise SystemExit("REFUSED: hostname mismatch")
    if config.get("network") != "192.168.2.0/24":
        raise SystemExit("REFUSED: unsupported network")
    if config.get("interface") != "eth0":
        raise SystemExit("REFUSED: unsupported interface")

    required = ("collector_state", "profile_state", "lock_path")
    if any(not isinstance(config.get(key), str)
           or not config[key].startswith("/") for key in required):
        raise SystemExit("REFUSED: invalid state paths")

    cooldown = config.get("cooldown_seconds")
    if type(cooldown) is not int or cooldown < 0:
        raise SystemExit("REFUSED: invalid cooldown")

    for key in ("mail_host", "mail_from", "mail_to"):
        value = config.get(key)
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f"REFUSED: invalid {key}")
        if "\\r" in value or "\\n" in value:
            raise SystemExit(f"REFUSED: invalid {key}")

    port = config.get("mail_port")
    if type(port) is not int or not 1 <= port <= 65535:
        raise SystemExit("REFUSED: invalid mail port")

    result = run_profile_once(
        config["collector_state"],
        config["profile_state"],
        config["lock_path"],
        subprocess.run,
        interface=config["interface"],
        cooldown=cooldown,
    )

    notification = deliver_next_notification(
        config["collector_state"],
        config["profile_state"],
        config["lock_path"],
        sender=config["mail_from"],
        recipient=config["mail_to"],
        host=config["mail_host"],
        port=config["mail_port"],
    )
    print(json.dumps({
        "scan": result if result is not None else {"status": "idle"},
        "notification": notification,
    }))


if __name__ == "__main__":
    main()
