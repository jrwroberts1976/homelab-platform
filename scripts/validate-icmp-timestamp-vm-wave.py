#!/usr/bin/env python3
"""Offline, non-mutating regression guard for three audited Debian VM targets."""
from pathlib import Path
import yaml
from jinja2 import Environment, StrictUndefined

root = Path(__file__).resolve().parents[1]
role = root / "IaC/ansible/roles/icmp_timestamp_vm_input"
helper = (role / "templates/helper.sh.j2").read_text()
unit = (role / "templates/homelab-icmp-timestamp-vm.service.j2").read_text()
tasks = (role / "tasks/main.yml").read_text()
cut = (root / "IaC/ansible/playbooks/greenbone-icmp-timestamp-vms-cutover.yml").read_text()
undo = (root / "IaC/ansible/playbooks/greenbone-icmp-timestamp-vms-rollback.yml").read_text()
targets = {
    "sensor-01": "192.168.2.55",
    "cloud-01": "192.168.2.53",
    "greenbone-01": "192.168.2.57",
}
deploy = yaml.safe_load(cut)[0]
rollback = yaml.safe_load(undo)[0]
assert deploy["serial"] == 1 and rollback["serial"] == 1
assert set(deploy["hosts"].split(":")) == set(targets)
assert deploy["vars"]["vm_icmp_expected_ips"] == targets
assert rollback["vars"]["vm_icmp_expected_ips"] == targets
assert "monitor-01" in cut and "monitor-01" in undo
assert "'monitor-01' if inventory_hostname == 'greenbone-01'" in cut
assert "hosts: greenbone-01" not in cut
assert "name: icmp_timestamp_vm_input" in cut
assert "vm_icmp_rule_before.rc == 1" in cut
assert "vm_icmp_rule_before.rc == 0" in cut
assert "homelab-icmp-vm-{{ inventory_hostname }}" in cut
assert "Unexpected mismatch between scanner response and exact tagged INPUT rule" in cut
for marker in ("ICMP_TIMESTAMP_RESULT=REPLY_CONFIRMED", "ICMP_TIMESTAMP_REPLIES_MATCHED=0",
               "VM_ICMP_ECHO=PASS", "VM_ICMP_TIMESTAMP=NO_REPLY_OBSERVED",
               "vm_icmp_containers_before", "vm_icmp_containers_after",
               "vm_icmp_sensor_services_before", "vm_icmp_sensor_services_after",
               "vm_icmp_rules_before", "vm_icmp_rules_after"):
    assert marker in cut, marker
assert "VM_ICMP_TIMESTAMP_ROLLBACK=APPLIED" in undo
assert "enabled: false" in undo and "state: stopped" in undo
assert "Before=docker.service" in unit
assert "ExecStop=" in unit and " remove" in unit
assert "state: restarted" not in cut and "state: restarted" not in tasks

engine = Environment(undefined=StrictUndefined)
for host, ip in targets.items():
    sh = engine.from_string(helper).render(
        icmp_timestamp_vm_target_ip=ip, inventory_hostname=host
    )
    assert f"TARGET={ip}/32" in sh
    assert f"COMMENT=homelab-icmp-vm-{host}" in sh
    assert "--icmp-type 13" in sh
    assert '"$IPTABLES" -w -I INPUT 1' in sh
    assert '"$IPTABLES" -w -D INPUT' in sh
    import subprocess
    check = subprocess.run(["/bin/sh", "-n"], input=sh, text=True,
                           capture_output=True, timeout=5)
    assert check.returncode == 0, check.stderr
    for unsafe in (" -F ", " -X ", " -P ", "-I FORWARD", "iptables-restore",
                   "nft flush", "systemctl restart"):
        assert unsafe not in sh, unsafe
for bad in ("ansible.builtin.apt:", "ansible.builtin.sysctl:", "state: restarted"):
    assert bad not in tasks
print("Audited three-VM scope, systemd persistence and helper shell render: PASS")
print("Host INPUT type-13-only rule, exact rollback, scanner and service checks: PASS")
print("Serial deployment preserves Docker FORWARD and sensor capture services: PASS")
print("No live host, kernel, firewall, Docker or Greenbone changes.")
