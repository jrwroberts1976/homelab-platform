#!/usr/bin/env python3
"""Offline regression test for the managed media firewall.

The approved default is now HTTPS-only. A temporary dual-port rollback is
represented in an explicit playbook, not the default policy. No host I/O.
"""
from pathlib import Path
from jinja2 import Environment, StrictUndefined

root = Path(__file__).resolve().parents[1]
role = root / "IaC/ansible/roles/media_firewall"
source = (role / "templates/nftables.conf.j2").read_text()
defaults = (role / "defaults/main.yml").read_text()

env = Environment(undefined=StrictUndefined)
def strict_bool(value):
    if not isinstance(value, bool):
        raise TypeError("Expected boolean firewall fixture")
    return value
env.filters["bool"] = strict_bool
render = env.from_string(source)
values = {
    "media_firewall_lan_subnet": "192.168.2.0/24",
    "media_firewall_dhcp_server_ipv4": "192.168.2.1",
    "media_firewall_backup_nfs_clients": ["192.168.2.70", "192.168.2.71"],
    "media_firewall_monitor_ipv4": "192.168.2.52",
    "media_firewall_qbittorrent_https_lan_enabled": True,
    "media_firewall_qbittorrent_http_lan_enabled": False,
    "media_firewall_icmp_timestamp_drop_enabled": True,
}
nft = render.render(**values)
rollback = render.render(**{**values, "media_firewall_qbittorrent_http_lan_enabled": True})
assert 'tcp dport 443 accept comment "LAN qBittorrent HTTPS"' in nft
assert "tcp dport 8081 accept" not in nft
assert 'tcp dport 8081 accept comment "LAN qBittorrent WebUI"' in rollback
for port in (22, 445, 1255, 1879, 2049, 9100):
    assert f"dport {port} " in nft, f"lost existing service port {port}"
assert "udp dport 1900" in nft
for ip in ("192.168.2.70", "192.168.2.71", "192.168.2.52"):
    assert ip in nft, f"lost NFS/monitoring peer {ip}"
assert "policy drop;" in nft
assert 'iifname "lo" accept' in nft
assert "media_firewall_qbittorrent_https_lan_enabled: true" in defaults
assert "media_firewall_qbittorrent_http_lan_enabled: false" in defaults
assert "media_firewall_icmp_timestamp_drop_enabled: true" in defaults
assert "icmp type timestamp-request drop" in nft

cutover = (root / "IaC/ansible/playbooks/qbittorrent-https-cutover.yml").read_text()
undo = (root / "IaC/ansible/playbooks/qbittorrent-https-http-rollback.yml").read_text()
assert "name: media_firewall" in cutover
assert "QBITTORRENT_DIRECT_LAN_HTTP_8081=BLOCKED" in cutover
assert "state: stopped" in cutover
assert "name: media_firewall" in undo
assert "QBITTORRENT_HTTP_ROLLBACK=PASS" in undo
assert "state: restarted" not in cutover and "state: restarted" not in undo

print("qBittorrent HTTPS-only LAN firewall template render: PASS")
print("Kodi, SSH, SMB, NFS and monitoring firewall invariants: PASS")
print("Loopback port 8081 preserved while new LAN connections blocked: PASS")
print("Explicit dual-port HTTP rollback: PASS")
print("No live firewall, DNS, services or scans changed.")
