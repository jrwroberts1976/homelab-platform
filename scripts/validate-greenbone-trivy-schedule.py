#!/usr/bin/env python3
"""Offline checks for the Greenbone feed/Trivy timing change (no host access)."""
from configparser import ConfigParser
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRIVY = ROOT / "IaC/ansible/roles/container_vulnerability_pilot/files/homelab-trivy-greenbone.timer"
SERVICE = ROOT / "IaC/ansible/roles/container_vulnerability_pilot/files/homelab-trivy-greenbone.service"
FEED = ROOT / "IaC/ansible/playbooks/greenbone-feed-refresh-timer.yml"
FULL = ROOT / "IaC/ansible/playbooks/greenbone-full-lan-weekly.yml"
DEFAULTS = ROOT / "IaC/ansible/roles/greenbone_scanning/defaults/main.yml"
CUTOVER = ROOT / "IaC/ansible/playbooks/trivy-greenbone-after-feed-timer.yml"

def read(path):
    return path.read_text(encoding="utf-8")

def main():
    config = ConfigParser(interpolation=None)
    config.read(TRIVY, encoding="utf-8")
    timer = config["Timer"]
    assert timer["OnCalendar"] == "*-*-* 19:00:00 UTC"
    assert timer["RandomizedDelaySec"] == "30m"
    assert timer["Persistent"].lower() == "false"
    assert timer["Unit"] == "homelab-trivy-greenbone.service"

    feed_code = read(FEED)
    full_code = read(FULL)
    defaults = read(DEFAULTS)
    assert 'greenbone_feed_calendar: "*-*-* 10:00:00"' in feed_code
    assert "TimeoutStartSec=10800" in feed_code
    assert 'greenbone_scanning_full_lan_schedule: "Sun *-*-* 12:00:00"' in full_code
    assert "greenbone_scanning_scan_timeout_seconds: 21600" in defaults
    assert "TimeoutStartSec={{ greenbone_scanning_scan_timeout_seconds + 900 }}" in read(
        ROOT / "IaC/ansible/roles/greenbone_scanning/templates/homelab-greenbone-full-lan-scan.service.j2"
    )

    # Conservatively compare UTC clocks to local configured scan times.
    # The UK summer-time shift makes the 10:00 and Sunday noon local jobs
    # start an hour *earlier* in UTC, so winter UTC is the worst case.
    feed_finish = timedelta(hours=10) + timedelta(seconds=10800)
    full_finish = timedelta(hours=12) + timedelta(seconds=21600 + 900)
    trivy_start = timedelta(hours=19)
    assert trivy_start > feed_finish
    assert trivy_start > full_finish
    assert trivy_start - full_finish >= timedelta(minutes=30)

    # The existing Trivy resource caps and fixed allowlist must stay in place.
    service = read(SERVICE)
    for value in (
        "MemoryMax=2G", "CPUQuota=50%", "TimeoutStartSec=180min",
        "ExecStart=/usr/local/sbin/homelab-trivy-pilot-scan",
        "ExecStartPost=/usr/local/sbin/homelab-container-estate-metrics",
        "TRIVY_ALLOW_EMPTY_IMAGES=",
    ):
        assert value in service, value

    cutover = read(CUTOVER)
    for value in (
        "hosts: greenbone-01",
        "greenbone_trivy_timer_change_approved | default(false) | bool",
        "ansible_host == '192.168.2.57'",
        "homelab-trivy-greenbone.timer",
        "backup: true",
        "daemon_reload: true",
        "state: restarted",
        "Persistent=false",
    ):
        assert value in cutover, value
    assert "homelab-trivy-greenbone.service\n        state: restarted" not in cutover

    print(
        "PASS: Trivy timer follows max feed/weekly-Greenbone windows; "
        "preserves scan resource guards; Ansible timer-only approval/rollback present"
    )

if __name__ == "__main__":
    main()
