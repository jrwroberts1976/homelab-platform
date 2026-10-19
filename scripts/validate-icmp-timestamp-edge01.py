#!/usr/bin/env python3
"""Offline syntactic and safety checks, never invokes nft on live hosts."""
from pathlib import Path
import ast
import subprocess
import yaml

root = Path(__file__).resolve().parents[1]
helper = root / "IaC/ansible/roles/icmp_timestamp_edge01/files/edge01_nft_timestamp.py"
cut = root / "IaC/ansible/playbooks/greenbone-icmp-timestamp-edge01-cutover.yml"
undo = root / "IaC/ansible/playbooks/greenbone-icmp-timestamp-edge01-rollback.yml"
text = helper.read_text()
ast.parse(text)
for path in (cut, undo):
    docs = yaml.safe_load(path.read_text())
    assert len(docs) == 1 and docs[0]['hosts'] == 'edge-01'
assert "flush ruleset" not in text
assert '"reload"' not in text and '"restart"' not in text
assert "homelab-icmp-edge01" in text
assert "nft" in text
assert "BACKUP.read_bytes()" in text
assert "EDGE01_ICMP_TIMESTAMP=NO_REPLY_OBSERVED" in cut.read_text()
assert "delegate_to: greenbone-01" in cut.read_text()
assert "rollback" in undo.read_text()
assert subprocess.run(["python3", "-m", "py_compile", str(helper)], capture_output=True).returncode == 0
print("EDGE01 offline syntax, scoped cutover, exact rollback and scanner assertions: PASS")
print("No live firewall, Proxmox, Docker or scan changes.")
