#!/usr/bin/env python3
"""Static safety gate for admin-01 controller deployment; never runs nft or systemctl."""
import ast
from pathlib import Path
import yaml

root = Path(__file__).resolve().parents[1]
source = root / "IaC/ansible/roles/icmp_timestamp_admin01/files/admin01-icmp-nft.py"
unit = root / "IaC/ansible/roles/icmp_timestamp_admin01/files/homelab-icmp-admin01.service"
cut = root / "IaC/ansible/playbooks/greenbone-icmp-admin01-cutover.yml"
undo = root / "IaC/ansible/playbooks/greenbone-icmp-admin01-rollback.yml"
code = source.read_text()
ast.parse(code)
compile(code, str(source), "exec")
assert 'TABLE = "homelab_icmp_timestamp"' in code
assert 'EXPECTED = "192.168.2.48/24"' in code
assert "corosync-qnetd" in cut.read_text()
assert "delegate_to: greenbone-01" in cut.read_text()
for file in (cut, undo):
    play = yaml.safe_load(file.read_text())
    assert len(play) == 1 and play[0]["hosts"] == "admin-01"
    assert play[0]["become"] is True
text = unit.read_text()
assert "ExecStart=/usr/local/sbin/homelab-icmp-admin01 apply" in text
assert "ExecStop=/usr/local/sbin/homelab-icmp-admin01 rollback" in text
assert "WantedBy=multi-user.target" in text
for path in (source, cut, undo, unit):
    txt = path.read_text()
    assert "nftables.service\n        state: started" not in txt
    assert "nft flush ruleset" not in txt
print("ADMIN01 STATIC SAFETY AND SYNTAX CHECK: PASS")
print("NOTE: no simulated live JSON/rule apply or rollback test has been completed.")
