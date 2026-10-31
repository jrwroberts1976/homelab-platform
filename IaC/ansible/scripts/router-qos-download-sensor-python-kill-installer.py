#!/usr/bin/env python3
"""Sensor-only real tc executor for the disposable independent-watchdog proof.

Invoked inside the shell harness's flock after the independent timer is armed.
This is NOT the production Phase 5 reconciler or a PPP hook. Deliberate SIGKILL
leaves partial namespace resources for the external watchdog to recover.
"""
import os
from pathlib import Path
import subprocess
import sys

NS = "qos-proof31"
BASE = Path("/run/qos-proof31")

def call(*argv):
    subprocess.run(argv, check=True, timeout=5)

def assert_environment():
    if os.geteuid() != 0 or subprocess.check_output(["hostname", "-s"], text=True).strip() != "sensor-01":
        raise RuntimeError("sensor root only")
    if (BASE / "owner").read_text().strip() != NS:
        raise RuntimeError("wrong owner")
    expected = int((BASE / "ns-inode").read_text().strip())
    actual = (Path("/run/netns") / NS).stat().st_ino
    host = Path("/proc/1/ns/net").stat().st_ino
    if actual != expected or actual == host:
        raise RuntimeError("namespace identity mismatch")
    if subprocess.run(["systemctl", "is-active", "--quiet", "qos-proof31-rollback.timer"]).returncode:
        raise RuntimeError("watchdog timer not active")
    # The independent watchdog and outer harness own creation and cleanup.
    # Refuse if any of the resources already exist.
    for argv in (
        ("ip", "netns", "exec", NS, "ip", "link", "show", "dev", "qi31"),
        ("ip", "netns", "exec", NS, "tc", "qdisc", "show", "dev", "qd31"),
    ):
        result = subprocess.run(argv, capture_output=True, text=True, timeout=5)
        if argv[-3:] == ("show", "dev", "qi31") and result.returncode == 0:
            raise RuntimeError("IFB collision")
        if "clsact" in result.stdout:
            raise RuntimeError("clsact collision")
    if not subprocess.run(["ip", "netns", "exec", NS, "ip", "link", "show", "dev", "qd31"], capture_output=True).returncode == 0:
        raise RuntimeError("dummy source missing")

def main():
    if sys.argv[1:] != ["--partial-kill"]:
        raise SystemExit("only --partial-kill test permitted")
    assert_environment()
    prefix = ("ip", "netns", "exec", NS)
    call(*prefix, "ip", "link", "add", "qi31", "type", "ifb")
    call(*prefix, "ip", "link", "set", "qi31", "up")
    call(*prefix, "tc", "qdisc", "add", "dev", "qi31", "root", "cake", "bandwidth", "43mbit", "besteffort", "flows")
    result = subprocess.run([*prefix, "tc", "qdisc", "show", "dev", "qi31"], capture_output=True, text=True, check=True)
    if "cake" not in result.stdout:
        raise RuntimeError("CAKE installation not verified")
    os.kill(os.getpid(), 9)

if __name__ == "__main__":
    main()
