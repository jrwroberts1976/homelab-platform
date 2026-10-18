#!/usr/bin/env python3
"""Offline render + mocked command-path tests for the Greenbone boot gate."""
import ast
from pathlib import Path
import types
from unittest.mock import patch
from jinja2 import Environment, StrictUndefined

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "IaC/ansible/roles/greenbone_scanning/templates"
VALUES = {
    "greenbone_scanning_runner": "/usr/local/sbin/homelab-greenbone-scan",
    "greenbone_scanning_readiness_runner": "/usr/local/sbin/homelab-greenbone-wait-ready",
    "greenbone_scanning_readiness_timeout_seconds": 1800,
    "greenbone_scanning_readiness_retry_seconds": 15,
    "greenbone_scanning_readiness_probe_timeout_seconds": 40,
    "greenbone_scanning_scan_timeout_seconds": 21600,
}
engine = Environment(undefined=StrictUndefined)
helper = engine.from_string(
    (TEMPLATES / "homelab-greenbone-wait-ready.py.j2").read_text()
).render(**VALUES)
ast.parse(helper)
service = engine.from_string(
    (TEMPLATES / "homelab-greenbone-managed-scan.service.j2").read_text()
).render(**VALUES)
assert "ExecStartPre=/usr/local/sbin/homelab-greenbone-wait-ready" in service
assert "ExecStart=/usr/local/sbin/homelab-greenbone-scan managed" in service
assert "TimeoutStartSec=24300" in service
assert "start_task" not in helper and "docker" not in helper.lower()
assert "managed\", \"--check\"" in helper

namespace = {"__name__": "greenbone_guard_test"}
exec(compile(helper, "boot_guard", "exec"), namespace)

class FakeClock:
    def __init__(self):
        self.current = 0
    def monotonic(self):
        return self.current
    def sleep(self, seconds):
        self.current += seconds

clock = FakeClock()
seen = []
def mocked_run(argv, **kwargs):
    seen.append(argv)
    assert argv == [
        "flock", "--nonblock", "/run/lock/homelab-greenbone-scan.lock",
        "/usr/local/sbin/homelab-greenbone-scan", "managed", "--check",
    ]
    assert kwargs["timeout"] <= 40
    if len(seen) == 1:
        return types.SimpleNamespace(returncode=1, stdout="")
    return types.SimpleNamespace(returncode=0, stdout="CHECK=PASS mode=managed task=mock")

with patch.object(namespace["subprocess"], "run", side_effect=mocked_run), \
     patch.object(namespace["time"], "monotonic", side_effect=clock.monotonic), \
     patch.object(namespace["time"], "sleep", side_effect=clock.sleep):
    assert namespace["wait_ready"]() == 0
assert len(seen) == 2 and clock.current == 15

print("Greenbone readiness gate Jinja render: PASS")
print("Greenbone readiness helper Python syntax: PASS")
print("Greenbone systemd ExecStartPre/timeout render: PASS")
print("Mocked non-scanning readiness retry: PASS")
print("No Docker helper, credentials, actual GMP request or scan started.")
