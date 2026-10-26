#!/usr/bin/env python3
"""Static safety checks for the staged Nextcloud EXR-deny mitigation.

Does not connect to hosts, build images, or change any configuration.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
ROLE = ROOT / "IaC/ansible/roles/cloud_stack"
TEMPLATE = ROLE / "templates/imagemagick-policy.xml.j2"
COMPOSE = ROLE / "templates/docker-compose.yml.j2"
DEFAULTS = ROLE / "defaults/main.yml"
TASKS = ROLE / "tasks/main.yml"
STAGE = ROOT / "IaC/ansible/playbooks/nextcloud-exr-hardening.yml"
ROLLBACK = ROOT / "IaC/ansible/playbooks/nextcloud-exr-rollback.yml"

policy = ET.fromstring(TEMPLATE.read_text())
observed = [
    tuple(element.get(key) for key in ("domain", "rights", "name", "pattern", "value"))
    for element in policy.findall("policy")
]
expected = [
    ("Undefined", "none", None, None, None),
    ("resource", None, "memory", None, "1024MiB"),
    ("resource", None, "map", None, "2048MiB"),
    ("resource", None, "area", None, "256MP"),
    ("resource", None, "disk", None, "2GiB"),
    ("resource", None, "width", None, "32KP"),
    ("resource", None, "height", None, "32KP"),
    ("path", "none", None, "@*", None),
    ("coder", "none", None, "URL", None),
    ("coder", "none", None, "HTTPS", None),
    ("coder", "none", None, "HTTP", None),
    ("coder", "none", None, "EXR", None),
]
assert observed == expected, "Changed ImageMagick policy; review original active restrictions"
compose = COMPOSE.read_text()
mount = "- {{ cloud_nextcloud_imagemagick_policy_path }}:/etc/ImageMagick-7/policy.xml:ro"
assert compose.count(mount) == 2, "Policy must be mounted read-only in app and cron"
assert compose.count("{% if cloud_nextcloud_exr_policy_enabled | bool %}") == 2
assert compose.count("{% endif %}") >= 2

defaults = DEFAULTS.read_text()
assert 'cloud_nextcloud_exr_policy_enabled: true' in defaults
assert 'cloud_nextcloud_image: "nextcloud:35.0.2-apache"' in defaults
assert "cloud_nextcloud_imagemagick_policy_path:" in defaults

tasks = TASKS.read_text()
assert tasks.index("Require explicit approval before cloud-01 deployment") < tasks.index(
    "Install hardened ImageMagick policy for Nextcloud"
)
assert tasks.index("Install hardened ImageMagick policy for Nextcloud") < tasks.index(
    "Install cloud-01 Docker Compose definition"
)

stage = STAGE.read_text()
rollback = ROLLBACK.read_text()
for text in (stage, rollback):
    assert "--no-deps --force-recreate app" in text
    assert "--no-deps --force-recreate cron" in text
    assert "127.0.0.1:8080" in text
    assert "nextcloud.home.jrwroberts.co.uk/status.php" in text
assert "nextcloud_exr_hardening_approved: false" in stage
assert "nextcloud_exr_rollback_approved: false" in rollback
assert "EXR read/write denied by policy" in stage
assert 'writeImage("EXR:/dev/null")' in stage, "Write-path test must use writeImage"
assert 'readImage("EXR:/dev/null")' in stage, "Read-path test must probe coder"
assert "nextcloud_exr_app_mount_present" in stage, "Restart must be avoidable on resume"
assert "already-hardened baseline" in stage, "Resume must accept approved policy"

print("PASS: EXR policy, restrictions, compose mounts, approval and rollback checks")
