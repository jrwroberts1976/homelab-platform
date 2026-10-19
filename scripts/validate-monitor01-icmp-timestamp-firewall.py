#!/usr/bin/env python3
"""Offline regression contract for monitor-01 timestamp-only filtering.

No host/network access and no configuration changes.
"""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
role = root / "IaC/ansible/roles/monitor_icmp_timestamp"
helper = role / "files/homelab-monitor01-icmp-timestamp"
sh = helper.read_text()
unit = (role / "files/homelab-monitor01-icmp-timestamp.service").read_text()
tasks = (role / "tasks/main.yml").read_text()
cutover = (root / "IaC/ansible/playbooks/greenbone-icmp-timestamp-monitor01-cutover.yml").read_text()
rollback = (root / "IaC/ansible/playbooks/greenbone-icmp-timestamp-monitor01-rollback.yml").read_text()
subprocess.run(["/bin/sh", "-n", str(helper)], check=True, timeout=5)

for entry in ("IPTABLES=/usr/sbin/iptables", "TARGET=192.168.2.52/32",
              "COMMENT=homelab-monitor01-icmp-timestamp", "nf_tables",
              '"$IPTABLES" -w -C INPUT', '"$IPTABLES" -w -I INPUT 1',
              '"$IPTABLES" -w -D INPUT', "--icmp-type 13", "RULE_REMOVED"):
    assert entry in sh, entry
for unsafe in (" -F ", " -X ", " -P ", "iptables-restore", "nft flush ruleset",
               "-I FORWARD", "-I DOCKER", "systemctl restart"):
    assert unsafe not in sh, unsafe

assert "Before=docker.service" in unit
assert "Type=oneshot" in unit and "RemainAfterExit=yes" in unit
assert " apply" in unit and " remove" in unit
assert "WantedBy=multi-user.target" in unit

for check in ("192.168.2.52", "nf_tables", "':INPUT ACCEPT '",
              "':FORWARD DROP '", "'-A FORWARD '", "DOCKER",
              "name: homelab-monitor01-icmp-timestamp.service",
              "enabled: true", "daemon_reload: true"):
    assert check in tasks, check
assert "state: restarted" not in tasks

for check in ("hosts: monitor-01", "hosts: greenbone-01",
              "name: monitor_icmp_timestamp",
              "ICMP_TIMESTAMP_RESULT=REPLY_CONFIRMED",
              "ICMP_TIMESTAMP_REPLIES_MATCHED=0",
              "MONITOR01_ICMP_ECHO=PASS",
              "MONITOR01_FIREWALL_SCOPE=HOST_INPUT_ONLY",
              "monitor01_containers_before", "monitor01_containers_after",
              "/opt/monitoring/docker-compose.yml",
              "https://grafana.home.jrwroberts.co.uk/",
              "':FORWARD DROP '"):
    assert check in cutover, check
assert "state: restarted" not in cutover
assert "hosts: monitor-01" in rollback and "hosts: greenbone-01" in rollback
assert "enabled: false" in rollback and "state: stopped" in rollback
assert "MONITOR01_ICMP_TIMESTAMP_ROLLBACK=APPLIED" in rollback
assert "state: restarted" not in rollback

print("monitor-01 host INPUT-only ICMP type-13 rule syntax and remove: PASS")
print("Docker Compose, Grafana HTTPS, container identity and FORWARD gates: PASS")
print("Scanner pre/post ICMP and explicit rollback contract: PASS")
print("No live host, firewall, monitoring services, sysctl or scans modified.")
