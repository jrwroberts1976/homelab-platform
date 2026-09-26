"""Static safety tests for intentionally inert monitor-01 refresh units."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2] / "ansible"
FILES = ROOT / "roles/network_host_enrichment/files"
GATE = ROOT / "playbooks/network-host-monitor01-refresh-units-stage.yml"


class DisabledRefreshStageTests(unittest.TestCase):
    def setUp(self):
        self.wrapper = (FILES / "homelab-proxmox-guest-refresh-wrapper").read_text()
        self.service = (FILES / "homelab-proxmox-guest-refresh.service").read_text()
        self.timer = (FILES / "homelab-proxmox-guest-refresh.timer").read_text()
        self.dropin = (FILES / "20-proxmox-guest-refresh.conf").read_text()
        self.gate = yaml.safe_load(GATE.read_text())[0]

    def test_single_target_and_never_runs_role(self):
        self.assertEqual(self.gate["hosts"], "monitoring_hosts")
        instructions = str(self.gate["tasks"])
        self.assertNotIn("ansible.builtin.import_role", instructions)
        self.assertIn("daemon_reload", instructions)
        self.assertNotIn("state: started", GATE.read_text())
        self.assertNotIn("enabled: true", GATE.read_text())

    def test_refresh_wrapper_uses_protected_bash_source(self):
        self.assertIn("set +x", self.wrapper)
        self.assertIn("set -euo pipefail", self.wrapper)
        self.assertIn(
            "source /etc/homelab-network-hosts/proxmox-api.env", self.wrapper
        )
        self.assertIn("PVE_TOKEN_SECRET", self.wrapper)
        self.assertIn(" --refresh", self.wrapper)
        self.assertNotIn("echo $PVE_TOKEN", self.wrapper)
        self.assertNotIn("curl", self.wrapper)
        self.assertNotIn("nmap", self.wrapper)

    def test_service_sandbox_and_disabled_periodic_unit(self):
        self.assertIn("Type=oneshot", self.service)
        self.assertIn("NoNewPrivileges=true", self.service)
        self.assertIn("ProtectSystem=strict", self.service)
        self.assertIn("ReadWritePaths=/var/lib/homelab-network-hosts", self.service)
        self.assertIn(
            "ReadWritePaths=/var/backups/homelab-network-migration/"
            "proxmox-guest-snapshots", self.service,
        )
        self.assertNotIn("EnvironmentFile", self.service)
        self.assertNotIn("WantedBy=", self.service)
        self.assertIn("Unit=homelab-proxmox-guest-refresh.service", self.timer)
        self.assertIn("OnUnitInactiveSec=6h", self.timer)
        self.assertIn("WantedBy=timers.target", self.timer)

    def test_enrichment_requires_refresh_and_explicit_cutover(self):
        self.assertIn(
            "Requires=homelab-proxmox-guest-refresh.service", self.dropin
        )
        self.assertIn(
            "After=homelab-proxmox-guest-refresh.service", self.dropin
        )
        self.assertIn(
            "ConditionPathExists=/etc/homelab-network-hosts/"
            "network-discovery-cutover-approved", self.dropin
        )
        self.assertIn("not marker_after.stat.exists", GATE.read_text())

    def test_existing_staged_files_hash_unchanged(self):
        data = GATE.read_text()
        for name in (
            "inventory.json", "deep-profiles.json",
            "enrichment.json", "proxmox-guests.json",
        ):
            self.assertIn(name, data)
        self.assertIn(
            "item[0].stat.checksum == item[1].stat.checksum", data
        )
        self.assertIn("rstrip=False", data)


if __name__ == "__main__":
    unittest.main()
