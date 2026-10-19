#!/usr/bin/env python3
"""Offline render/contract checks for staged qBittorrent HTTPS. No host I/O."""
from pathlib import Path

from jinja2 import Environment, StrictUndefined

root = Path(__file__).resolve().parents[1]
role = root / "IaC/ansible/roles/qbittorrent_https"
template = (role / "templates/nginx-qbittorrent.conf.j2").read_text()
values = {
    "qbittorrent_https_fqdn": "qbittorrent.home.jrwroberts.co.uk",
    "qbittorrent_https_backend": "127.0.0.1",
    "qbittorrent_https_backend_port": 8081,
    "qbittorrent_https_certificate_fullchain":
        "/etc/letsencrypt/live/qbittorrent.home.jrwroberts.co.uk/fullchain.pem",
    "qbittorrent_https_certificate_key":
        "/etc/letsencrypt/live/qbittorrent.home.jrwroberts.co.uk/privkey.pem",
}
rendered = Environment(undefined=StrictUndefined).from_string(template).render(**values)
assert "server_name qbittorrent.home.jrwroberts.co.uk;" in rendered
assert "proxy_pass http://127.0.0.1:8081;" in rendered
assert "proxy_set_header Host $proxy_host;" in rendered
assert "proxy_cookie_flags ~ secure;" in rendered
assert "ssl_certificate /etc/letsencrypt/live/qbittorrent." in rendered
assert "listen 80;" not in rendered

tasks = (role / "tasks/main.yml").read_text()
assert "qBittorrent, Kodi, SMB and NFS were not restarted." in tasks
assert "Legacy 8081 LAN rule remains enabled" in tasks
assert "state: restarted" not in tasks
play = (
    root / "IaC/ansible/playbooks/qbittorrent-https-stage.yml"
).read_text()
assert "homelab_certificate" in play
assert "qbittorrent_https" in play
assert "media_firewall" not in play
assert "Refuse provisioning if either Pi-hole resolver lacks" in play
dns = (
    root / "IaC/ansible/roles/dns_resolver/defaults/main.yml"
).read_text()
assert (
    "192.168.2.195 media-01.jameshouse media-01 "
    "qbittorrent.home.jrwroberts.co.uk"
) in dns

print("qBittorrent HTTPS reverse-proxy template render: PASS")
print("qBittorrent HTTPS source / safety contracts: PASS")
print("No host deployment or firewall cutover performed.")
