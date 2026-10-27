#!/usr/bin/env python3
"""Static guarantee that the CVE triage playbook cannot change running hosts."""
from pathlib import Path
import re

root=Path(__file__).resolve().parent.parent
p=root/"IaC/ansible/playbooks/security-container-triage-readonly.yml"
s=p.read_text()
assert 'serial: 1' in s
assert 'changed_when: false' in s
assert 'hosts: "monitor-01:komodo-01:cloud-01:docker-01:greenbone-01"' in s
assert 'ansible_facts.hostname == inventory_hostname' in s
assert 'summary.get("complete") is True' in s
assert 'now-completed <= 30*3600' in s
assert 'running == set(entries)' in s
assert 'entry.get("image_id")==image_id' in s
assert 'report.get("Metadata",{}).get("ImageID")==image_id' in s
assert 'observed[sev]==counts[sev]' in s
assert 'TRIVY_TRIAGE_READONLY=PASS' in s
for token in (
    "docker ps", "docker compose up", "docker pull", "docker run",
    "systemctl start", "apt install", "apt upgrade", "reboot",
    "ansible.builtin.copy", "ansible.builtin.template", "ansible.builtin.apt",
    "ansible.builtin.systemd", "ansible.builtin.shell",
):
    assert token not in s, token
assert not re.search(r"(?m)^\s+become_user:\s*",s)
assert s.count("ansible.builtin.command:") == 1
print("PASS: read-only validated all-host Trivy root-cause summary, serial, bounded")
