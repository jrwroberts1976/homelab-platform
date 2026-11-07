#!/usr/bin/env python3
"""Offline plan for router-local DHCP rollback timer.

Does not execute systemd commands.
"""

import json

UNIT = "homelab-dhcp-infinite-recovery"
WORKER = (
    "/usr/local/libexec/homelab/"
    "router_dhcp_infinite_rollback_worker.py"
)

def plan():
    return {
        "arm": [
            "/usr/bin/systemd-run",
            "--unit=" + UNIT,
            "--on-active=5m",
            "--timer-property=AccuracySec=1s",
            "/usr/bin/python3",
            WORKER,
            "--execute-approved-rollback",
        ],
        "verify": [
            "/usr/bin/systemctl",
            "is-active",
            "--quiet",
            UNIT + ".timer",
        ],
        "cancel": [
            "/usr/bin/systemctl",
            "stop",
            UNIT + ".timer",
        ],
    }

if __name__ == "__main__":
    print(json.dumps(plan(), indent=2))
