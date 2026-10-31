#!/usr/bin/env python3
"""Sensor-only read-only namespace inspection. No network mutations.

Returns INCONCLUSIVE when the historical disposable namespace is absent.
Never authorizes journal recovery. Restricted to fixed namespace/interface IDs.
"""
import json
from pathlib import Path
import subprocess

NS = "qos-proof31"

def run(argv):
    return subprocess.run(argv, capture_output=True, text=True, timeout=5, check=False)

def collect():
    host = run(["hostname", "-s"])
    if host.returncode or host.stdout.strip() != "sensor-01":
        raise RuntimeError("sensor-only inspection")
    ns = Path("/run/netns/qos-proof31")
    owner = Path("/run/qos-proof31/ns-inode")
    if not ns.exists() or not owner.is_file() or owner.is_symlink():
        return {"status": "INCONCLUSIVE_NAMESPACE_OR_OWNER_ABSENT",
                "journal_recovery_authorized": False, "network_modified": False}
    namespace_inode = ns.stat().st_ino
    host_inode = Path("/proc/1/ns/net").stat().st_ino
    recorded = owner.read_text(encoding="utf-8").strip()
    if not recorded.isdecimal() or namespace_inode != int(recorded) or namespace_inode == host_inode:
        return {"status": "REFUSE_NAMESPACE_MISMATCH",
                "journal_recovery_authorized": False, "network_modified": False}
    observations = {}
    for key, cmd in (
        ("source", ["ip", "link", "show", "dev", "qd31"]),
        ("ifb", ["ip", "link", "show", "dev", "qi31"]),
        ("filter", ["tc", "filter", "show", "dev", "qd31", "ingress"]),
        ("qdisc", ["tc", "qdisc", "show", "dev", "qd31"]),
    ):
        result = run(["ip", "netns", "exec", NS, *cmd])
        observations[key] = {"rc": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    return {"status": "OBSERVED_NOT_AUTHORIZED", "namespace_inode": namespace_inode,
            "host_inode": host_inode, "recorded_inode": int(recorded),
            "observations": observations,
            "journal_recovery_authorized": False, "network_modified": False}

if __name__ == "__main__":
    print(json.dumps(collect(), sort_keys=True))
