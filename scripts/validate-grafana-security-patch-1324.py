#!/usr/bin/env python3
"""Static offline checks for bounded Grafana 13.2.4 security patch.

Run from repository root. This script never contacts remote hosts.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DEFAULTS = ROOT / "IaC/ansible/roles/monitoring_stack/defaults/main.yml"
ALT_COMPOSE = ROOT / "IaC/komodo/stacks/monitoring/compose.yml"
TEMPLATE = ROOT / "IaC/ansible/roles/monitoring_stack/templates/docker-compose.yml.j2"
PLAY = ROOT / "IaC/ansible/playbooks/grafana-security-patch-1324.yml"

def main():
    defaults = DEFAULTS.read_text()
    alt = ALT_COMPOSE.read_text()
    template = TEMPLATE.read_text()
    play = PLAY.read_text()

    assert "monitoring_grafana_image: grafana/grafana:13.2.4" in defaults
    assert "monitoring_grafana_image: grafana/grafana:13.2.1" not in defaults
    assert "image: grafana/grafana:13.2.4" in alt
    assert "image: grafana/grafana:13.2.1" not in alt
    assert "image: {{ monitoring_grafana_image }}" in template
    assert 'hosts: monitor-01' in play
    assert 'grafana_security_patch_approved | default(false) | bool' in play
    assert "monitoring_grafana_image == grafana_patch_new_image" in play
    assert "grafana_patch_old_image: \"grafana/grafana:13.2.1\"" in play
    assert "grafana_patch_new_image: \"grafana/grafana:13.2.4\"" in play
    assert "ansible_facts.default_ipv4.address == '192.168.2.52'" in play
    assert "13.2.1" in play and "13.2.4" in play

    for guard in (
        'data mount', 'database exists', 'online SQLite backup',
        'PRAGMA quick_check', 'backup: true', 'mode: "0600"',
        'url: http://127.0.0.1:3000/api/health',
        "--no-deps", "--no-build", "--force-recreate",
        "other monitoring containers", "grafana_patch_other_before",
        "grafana_patch_other_after",
    ):
        assert guard.lower() in play.lower(), guard

    # Prevent a broad redeploy of the monitoring stack or unreviewed apt changes.
    assert "playbooks/monitoring.yml" not in play
    assert "--remove-orphans" not in play
    assert "docker compose down" not in play
    assert "apt-get upgrade" not in play
    assert "reboot" not in play.lower()
    assert not re.search(r"(?m)^\s*roles:\s*$", play)
    assert re.search(r"(?m)^\s*- grafana\s*$", play)
    assert not re.search(r"(?m)^\s*- (?:prometheus|loki|alertmanager|blackbox)\s*$", play)
    print("PASS: Grafana 13.2.4 patch is separately approved, backed up and service-only")

if __name__ == "__main__":
    main()
