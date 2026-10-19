#!/usr/bin/env python3
"""Validate the one-host Greenbone ICMP timestamp diagnostic offline."""
import ast
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
script = root / "IaC/ansible/playbooks/files/icmp-timestamp-probe.py"
playbook = root / "IaC/ansible/playbooks/greenbone-icmp-timestamp-media01-readonly.yml"
source = script.read_text()
play = playbook.read_text()
ast.parse(source)
tested = subprocess.run(
    [sys.executable, str(script), "--self-test"],
    capture_output=True, text=True, timeout=10, check=True,
)
assert "ICMP_TIMESTAMP_PROBE_SELF_TEST=PASS" in tested.stdout
assert "hosts: greenbone-01" in play
assert "192.168.2.195" in play
assert "192.168.2.57" in play
assert "changed_when: false" in play
assert "ICMP_TIMESTAMP_RESULT=REPLY_CONFIRMED" in play
assert "NO_TIMESTAMP_REPLY_OBSERVED_NOT_PROOF_OF_FIX" in play
for unsafe in ("state: restarted", "state: stopped", "sysctl:", "nft -f", "iptables -I"):
    assert unsafe not in play, unsafe
print("RFC 792 timestamp packet and matching reply self-test: PASS")
print("One-host read-only Ansible probe scope and result markers: PASS")
print("No firewall, sysctl, service, risk allowlist or Greenbone scan changes.")
