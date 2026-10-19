#!/usr/bin/env python3
"""Offline scope and rollback checks for docker-01 ICMP timestamp hardening.

No SSH connections, service changes, firewall commands, or Git changes.
"""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
role = root / "IaC/ansible/roles/docker_icmp_timestamp"
script = (role / "files/homelab-docker01-icmp-timestamp").read_text()
unit = (role / "files/homelab-docker01-icmp-timestamp.service").read_text()
tasks = (role / "tasks/main.yml").read_text()
deploy = (root / "IaC/ansible/playbooks/greenbone-icmp-timestamp-docker01-cutover.yml").read_text()
rollback = (root / "IaC/ansible/playbooks/greenbone-icmp-timestamp-docker01-rollback.yml").read_text()

subprocess.run(["/bin/sh", "-n", str(role / "files/homelab-docker01-icmp-timestamp")],
               check=True, timeout=5)
assert "IPTABLES=/usr/sbin/iptables" in script
assert "TARGET=192.168.2.220/32" in script
assert "grep -q '(nf_tables)'" in script
assert '"$IPTABLES" -w -C INPUT' in script
assert '"$IPTABLES" -w -I INPUT 1' in script
assert '"$IPTABLES" -w -D INPUT' in script
assert "--icmp-type 13" in script
assert "-m comment --comment" in script
for unsafe in (" -F ", " -X ", " -P ", "iptables-restore", "nft flush ruleset", "-I FORWARD", "-I DOCKER"):
    assert unsafe not in script, unsafe

assert "Type=oneshot" in unit
assert "RemainAfterExit=yes" in unit
assert "Before=docker.service" in unit
assert "ExecStart=" in unit and " apply" in unit
assert "ExecStop=" in unit and " remove" in unit
assert "WantedBy=multi-user.target" in unit
assert "daemon_reload: true" in tasks
assert "enabled: true" in tasks
assert "nf_tables" in tasks
assert "':FORWARD DROP '" in tasks
assert "name: docker.service" not in tasks
assert "state: restarted" not in tasks

assert "hosts: docker-01" in deploy and "hosts: greenbone-01" in deploy
assert "name: docker_icmp_timestamp" in deploy
assert "ICMP_TIMESTAMP_RESULT=REPLY_CONFIRMED" in deploy
assert "ICMP_TIMESTAMP_RESULT=NO_REPLY_OBSERVED" in deploy
assert "DOCKER01_ICMP_ECHO=PASS" in deploy
assert "docker01_containers_before" in deploy and "docker01_containers_after" in deploy
assert "https://birdnet.home.jrwroberts.co.uk/" in deploy
assert "state: restarted" not in deploy
assert "hosts: docker-01" in rollback and "hosts: greenbone-01" in rollback
assert "enabled: false" in rollback and "state: stopped" in rollback
assert "DOCKER01_ICMP_TIMESTAMP_ROLLBACK=APPLIED" in rollback
assert "docker.service" in rollback

print("iptables-nft host INPUT type-13-only rule, idempotence and removal: PASS")
print("Dedicated reboot-persistent unit and Docker chain preservation: PASS")
print("Scanner pre/post checks, BirdNET access and scoped rollback: PASS")
print("No live Docker, firewall, service, scan or accepted-risk changes.")
