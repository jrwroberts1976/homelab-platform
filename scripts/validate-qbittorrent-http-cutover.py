#!/usr/bin/env python3
"""Offline contract checks for approved qBittorrent LAN HTTP/8081 cutover.

This validates templates and both explicit modes. No host access or changes.
"""
from pathlib import Path
from jinja2 import Environment, StrictUndefined

root = Path(__file__).resolve().parents[1]
role = root / "IaC/ansible/roles/media_firewall"
template = (role / "templates/nftables.conf.j2").read_text()
defaults = (role / "defaults/main.yml").read_text()
role_tasks = (role / "tasks/main.yml").read_text()
cutover = (root / "IaC/ansible/playbooks/qbittorrent-https-cutover.yml").read_text()
rollback = (root / "IaC/ansible/playbooks/qbittorrent-https-http-rollback.yml").read_text()

env = Environment(undefined=StrictUndefined)
def strict_bool(value):
    if not isinstance(value, bool):
        raise TypeError("Expected typed boolean firewall setting")
    return value
env.filters["bool"] = strict_bool
render = env.from_string(template)
base = {
    "media_firewall_lan_subnet": "192.168.2.0/24",
    "media_firewall_dhcp_server_ipv4": "192.168.2.1",
    "media_firewall_backup_nfs_clients": ["192.168.2.70", "192.168.2.71"],
    "media_firewall_monitor_ipv4": "192.168.2.52",
    "media_firewall_qbittorrent_https_lan_enabled": True,
}
new = render.render(**{**base, "media_firewall_qbittorrent_http_lan_enabled": False})
old = render.render(**{**base, "media_firewall_qbittorrent_http_lan_enabled": True})

assert "media_firewall_qbittorrent_https_lan_enabled: true" in defaults
assert "media_firewall_qbittorrent_http_lan_enabled: false" in defaults
assert 'tcp dport 443 accept comment "LAN qBittorrent HTTPS"' in new
assert "tcp dport 8081 accept" not in new
assert 'tcp dport 8081 accept comment "LAN qBittorrent WebUI"' in old
assert 'iifname "lo" accept' in new
assert "policy drop;" in new
for port in (22, 445, 1255, 1879, 2049, 9100):
    assert f"dport {port} " in new, f"Existing service lost: {port}"
assert "udp dport 1900" in new
for client in ("192.168.2.70", "192.168.2.71", "192.168.2.52"):
    assert client in new
assert "tcp dport 8081" in role_tasks
assert "media_firewall_qbittorrent_http_lan_enabled | bool" in role_tasks

for name, src, flag in [
    ("cutover", cutover, "media_firewall_qbittorrent_http_lan_enabled: false"),
    ("rollback", rollback, "media_firewall_qbittorrent_http_lan_enabled: true"),
]:
    assert "hosts: media_hosts" in src, name
    assert "name: media_firewall" in src, name
    assert flag in src, name
    assert "state: restarted" not in src, name

assert "state: stopped" in cutover
assert "host: 192.168.2.195" in cutover
assert "QBITTORRENT_LAN_HTTPS=PASS" in cutover
assert "QBITTORRENT_LOOPBACK_HTTP_8081=AVAILABLE" in cutover
assert "QBITTORRENT_HTTP_ROLLBACK=PASS" in rollback
print("HTTPS-only nftables rendering and preserved LAN/NFS service rules: PASS")
print("LAN TCP/8081 blocked while local qBittorrent port stays reachable: PASS")
print("Explicit dual-port rollback policy: PASS")
print("Scoped cutover and rollback Ansible contract: PASS")
print("No live firewall or service changes performed.")
