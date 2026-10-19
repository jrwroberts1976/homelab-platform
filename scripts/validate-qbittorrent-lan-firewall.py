#!/usr/bin/env python3
"""Offline check for staged media-01 HTTPS firewall. Does not modify hosts."""
from pathlib import Path

from jinja2 import Environment, StrictUndefined

root = Path(__file__).resolve().parents[1]
role = root / "IaC/ansible/roles/media_firewall"
source = (role / "templates/nftables.conf.j2").read_text()
defaults = (role / "defaults/main.yml").read_text()
values = {
    "media_firewall_lan_subnet": "192.168.2.0/24",
    "media_firewall_dhcp_server_ipv4": "192.168.2.1",
    "media_firewall_backup_nfs_clients": ["192.168.2.70", "192.168.2.71"],
    "media_firewall_monitor_ipv4": "192.168.2.52",
    "media_firewall_qbittorrent_https_lan_enabled": True,
    "media_firewall_qbittorrent_http_lan_enabled": True,
}
render = Environment(undefined=StrictUndefined).from_string(source)
nft = render.render(**values)
assert 'tcp dport 443 accept comment "LAN qBittorrent HTTPS"' in nft
assert 'tcp dport 8081 accept comment "LAN qBittorrent WebUI"' in nft
for port in (22, 445, 1900, 1255, 1879, 2049, 9100):
    assert f"dport {port} " in nft, f"lost existing service port {port}"
for ip in ("192.168.2.70", "192.168.2.71", "192.168.2.52"):
    assert ip in nft, f"lost backup/monitoring peer {ip}"
assert "policy drop;" in nft
assert "media_firewall_qbittorrent_https_lan_enabled: true" in defaults
assert "media_firewall_qbittorrent_http_lan_enabled: true" in defaults

# Future phase is intentionally possible, but NOT enabled by this commit.
future = render.render(**{**values, "media_firewall_qbittorrent_http_lan_enabled": False})
assert 'dport 8081 accept' not in future
assert 'dport 443 accept' in future
stage = (
    root / "IaC/ansible/playbooks/qbittorrent-https-lan-stage.yml"
).read_text()
assert "role: media_firewall" in stage
assert "QBITTORRENT_LAN_HTTPS=PASS" in stage
assert "QBITTORRENT_LEGACY_HTTP=AVAILABLE" in stage
assert "state: restarted" not in stage
assert "192.168.2.195:8081" in stage
print("qBittorrent LAN 443 + 8081 firewall template render: PASS")
print("Kodi, SSH, SMB, NFS and monitoring firewall invariants: PASS")
print("Explicit future no-8081 template option: PASS")
print("LAN/controller HTTPS and HTTP rollback check path: PASS")
print("No live firewall, DNS, services or scans changed.")
