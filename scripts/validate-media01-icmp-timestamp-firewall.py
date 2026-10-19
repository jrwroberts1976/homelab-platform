#!/usr/bin/env python3
"""Offline ICMPv4 timestamp rule and no-regression checks for media-01.
No host modifications or outbound network traffic.
"""
from pathlib import Path
from jinja2 import Environment, StrictUndefined
root = Path(__file__).resolve().parents[1]
role = root / "IaC/ansible/roles/media_firewall"
defaults = (role / "defaults/main.yml").read_text()
source = (role / "templates/nftables.conf.j2").read_text()
tasks = (role / "tasks/main.yml").read_text()
deploy = (root / "IaC/ansible/playbooks/greenbone-icmp-timestamp-media01-cutover.yml").read_text()
rollback = (root / "IaC/ansible/playbooks/greenbone-icmp-timestamp-media01-rollback.yml").read_text()
e = Environment(undefined=StrictUndefined)
def strict_bool(v):
    if not isinstance(v, bool):
        raise ValueError("Expected typed boolean")
    return v
e.filters["bool"] = strict_bool
values = {
    "media_firewall_lan_subnet": "192.168.2.0/24",
    "media_firewall_dhcp_server_ipv4": "192.168.2.1",
    "media_firewall_backup_nfs_clients": ["192.168.2.70", "192.168.2.71"],
    "media_firewall_monitor_ipv4": "192.168.2.52",
    "media_firewall_qbittorrent_https_lan_enabled": True,
    "media_firewall_qbittorrent_http_lan_enabled": False,
}
template = e.from_string(source)
with_drop = template.render(**{**values, "media_firewall_icmp_timestamp_drop_enabled": True})
without_drop = template.render(**{**values, "media_firewall_icmp_timestamp_drop_enabled": False})
rule = 'icmp type timestamp-request drop comment "Block ICMPv4 timestamp requests"'
assert "media_firewall_icmp_timestamp_drop_enabled: true" in defaults
assert with_drop.count(rule) == 1
assert rule not in without_drop
assert with_drop.index(rule) < with_drop.index("ct state established,related accept")
assert with_drop.index(rule) < with_drop.index("ip protocol icmp accept")
assert "ip protocol icmp accept" in with_drop and "meta l4proto ipv6-icmp accept" in with_drop
assert "iifname \"lo\" accept" in with_drop
for item in ("ct state invalid drop", "ct state established,related accept", "policy drop;",
             "tcp dport 22 accept", "tcp dport 445 accept", "tcp dport 443 accept",
             "udp dport 1900 accept", "tcp dport 1255 accept", "tcp dport 1879 accept",
             "tcp dport 2049 accept", "tcp dport 9100 accept"):
    assert item in with_drop and item in without_drop, item
for peer in ("192.168.2.70", "192.168.2.71", "192.168.2.52"):
    assert peer in with_drop
assert "tcp dport 8081 accept" not in with_drop and "tcp dport 8081 accept" not in without_drop
assert "media_firewall_icmp_timestamp_drop_enabled is boolean" in tasks
assert "'icmp type timestamp-request drop' in media_firewall_ruleset.stdout" in tasks
for src,flag in [(deploy,"media_firewall_icmp_timestamp_drop_enabled: true"),
                 (rollback,"media_firewall_icmp_timestamp_drop_enabled: false")]:
    assert "hosts: media-01" in src and "hosts: greenbone-01" in src
    assert flag in src and "name: media_firewall" in src
    assert "media_firewall_qbittorrent_http_lan_enabled: false" in src
    assert "state: restarted" not in src
assert "REPLY_CONFIRMED" in deploy and "NO_REPLY_OBSERVED" in deploy
assert "MEDIA01_ICMP_ECHO=PASS" in deploy
assert "MEDIA01_ICMP_TIMESTAMP_ROLLBACK=APPLIED" in rollback
print("media-01 ICMPv4 timestamp-only drop/rollback template render: PASS")
print("Established, ping, ICMPv6, loopback, HTTPS-only and NFS invariants: PASS")
print("Scoped scanner pre/post probes and manual rollback: PASS")
print("No live firewall, services, DNS, kernel or scan modified.")
