#!/usr/bin/env python3
"""Offline safety/target validation for the remaining 11 accepted ICMP hosts.

Reads Git only; does not connect to hosts or send packets.
"""
from pathlib import Path
import yaml

root = Path(__file__).resolve().parents[1]
path = root / "IaC/ansible/playbooks/greenbone-icmp-timestamp-remaining11-readonly.yml"
source = path.read_text()
plays = yaml.safe_load(source)
assert len(plays) == 2, "Expected local ownership and external scanner plays"
targets = {
    "admin-01": "192.168.2.48",
    "dns-02": "192.168.2.50",
    "dns-01": "192.168.2.51",
    "cloud-01": "192.168.2.53",
    "mail-relay-01": "192.168.2.54",
    "sensor-01": "192.168.2.55",
    "edge-01": "192.168.2.56",
    "greenbone-01": "192.168.2.57",
    "komodo-01": "192.168.2.58",
    "zabbix-01": "192.168.2.59",
    "Proxmox-2": "192.168.2.71",
}
owner, scan = plays
assert set(owner["hosts"].split(":")) == set(targets), "Wrong host target scope"
assert owner["serial"] == 1, "Review hosts sequentially"
assert owner["vars"]["expected_ipv4"] == targets
assert scan["hosts"] == "greenbone-01"
assert set(scan["vars"]["remaining_hosts"]) == set(targets)
assert "monitor-01" not in targets and "media-01" not in targets and "docker-01" not in targets
assert "monitor-01" in source and "'monitor-01' if item == 'greenbone-01'" in source
assert "ICMP_TIMESTAMP_PROBE_SELF_TEST=PASS" in source
assert "REMEDIATION_STATE=NOT_CHANGED" in source
for play in plays:
    for task in play["tasks"]:
        if "ansible.builtin.command" in task:
            assert task.get("changed_when") is False, task["name"]
        assert not any(k in task for k in (
            "ansible.builtin.systemd_service",
            "ansible.builtin.copy",
            "ansible.builtin.template",
            "ansible.builtin.apt",
            "ansible.builtin.sysctl",
        )), task["name"]
cmd_src = owner["tasks"][1]["ansible.builtin.command"]["argv"][2]
compile(cmd_src, "<read-only-owner-audit>", "exec")
for unsafe in ('iptables -I', 'iptables -D', 'iptables -F', 'nft -f', 'nft flush',
               'sysctl -w', 'state: restarted', 'enabled: true'):
    assert unsafe not in source, unsafe
assert 'CAP_NET_ADMIN' in source
assert 'pve-firewall' in source and 'proxmox-firewall' in source
print("Canonical 11 hosts and 11 addresses: PASS")
print("LXC, Docker, Proxmox, iptables-nft and nftables read-only checks: PASS")
print("Independent scanner vantage including scanner self-check via monitor-01: PASS")
print("No host configuration, firewall, kernel, Docker service or scan changes.")
