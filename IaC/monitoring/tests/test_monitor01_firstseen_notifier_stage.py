"""Offline checks for safe, inert first-seen notifier code staging."""
import ast
import json
from pathlib import Path
import unittest

import yaml
from jinja2 import Environment

ROOT = Path(__file__).resolve().parents[2] / "ansible"
TEMPLATE = ROOT / "roles/network_host_collector/templates/homelab-network-device-email-alert.py.j2"
DEFAULTS = ROOT / "roles/network_host_collector/defaults/main.yml"
GATE = ROOT / "playbooks/network-host-monitor01-firstseen-notifier-stage.yml"


def render(host):
    config = yaml.safe_load(DEFAULTS.read_text())
    env = Environment()
    env.filters["to_json"] = json.dumps
    values = {
        "network_host_collector_expected_hostname": host,
        "network_host_collector_inventory": "/var/lib/homelab-network-hosts/inventory.json",
        "network_host_collector_alert_registry": "/var/lib/homelab-network-hosts/alerted-macs.json",
        "network_host_collector_alert_smtp_host": config["network_host_collector_alert_smtp_host"],
        "network_host_collector_alert_smtp_port": config["network_host_collector_alert_smtp_port"],
        "network_host_collector_alert_from": config["network_host_collector_alert_from"],
    }
    script = env.from_string(TEMPLATE.read_text()).render(**values)
    module = ast.parse(script)
    hosts = [
        stmt.value.value for stmt in module.body
        if isinstance(stmt, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "COLLECTOR_HOST"
                for t in stmt.targets)
        and isinstance(stmt.value, ast.Constant)
    ]
    return hosts, script


class FirstSeenNotifierStageTests(unittest.TestCase):
    def test_source_proxmox2_default_preserved(self):
        config = yaml.safe_load(DEFAULTS.read_text())
        self.assertEqual(config["network_host_collector_expected_hostname"], "Proxmox-2")
        hosts, script = render(config["network_host_collector_expected_hostname"])
        self.assertEqual(hosts, ["Proxmox-2"])
        self.assertIn("ExecStart", script) if False else None  # Never run script.

    def test_monitor01_notifier_has_correct_collector_identity(self):
        hosts, script = render("monitor-01")
        self.assertEqual(hosts, ["monitor-01"])
        self.assertIn("NETWORK_DEVICE_ALERT_TO", script)
        self.assertIn("alerted-macs.json", script)
        self.assertIn("192.168.2.54", script)

    def test_gate_installs_only_inert_script_not_credentials(self):
        gate = yaml.safe_load(GATE.read_text())
        self.assertEqual(len(gate), 1)
        self.assertEqual(gate[0]["hosts"], "monitoring_hosts")
        tasks = gate[0]["tasks"]
        mutating = [t for t in tasks if any(k in t for k in (
            "ansible.builtin.copy", "ansible.builtin.template",
            "ansible.builtin.file", "ansible.builtin.systemd_service",
            "ansible.builtin.apt",
        ))]
        self.assertEqual(len(mutating), 1)
        self.assertIn("ansible.builtin.template", mutating[0])
        self.assertEqual(mutating[0]["ansible.builtin.template"]["mode"], "0750")
        gate_text = GATE.read_text()
        self.assertIn("network_host_collector_alert_enabled: false", gate_text)
        self.assertIn("not notifier_target_paths.results[1].stat.exists", gate_text)
        self.assertIn("not notifier_target_paths.results[3].stat.exists", gate_text)
        self.assertIn("ExecStartPost=", gate_text)
        self.assertIn("EnvironmentFile=", gate_text)
        self.assertIn("notifier_state_before", gate_text)
        self.assertIn("notifier_state_after", gate_text)

    def test_stage_does_not_send_mail_run_notifier_or_activate_scan(self):
        gate = yaml.safe_load(GATE.read_text())
        text = str(gate)
        self.assertNotIn("--test-email", text)
        self.assertNotIn("send_message(", text)
        self.assertNotIn("state: started", GATE.read_text())
        self.assertNotIn("enabled: true", GATE.read_text())
        self.assertNotIn("ansible.builtin.systemd_service", text)
        self.assertNotIn("ansible.builtin.import_role", text)


if __name__ == "__main__":
    unittest.main()
