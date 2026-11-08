#!/usr/bin/env python3
"""Small source guards for the KISS SSH transport setup and rollback."""
import unittest
from pathlib import Path

PLAYBOOKS = Path(__file__).resolve().parents[1] / "playbooks"


class SSHTransportPlaybookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.setup = (PLAYBOOKS / "passive-os-ssh-transport-setup.yml").read_text()
        cls.rollback = (PLAYBOOKS / "passive-os-ssh-transport-rollback.yml").read_text()

    def test_default_denies_changes(self):
        self.assertIn("passive_os_transport_apply: false", self.setup)
        self.assertIn("passive_os_transport_apply | bool", self.setup)
        self.assertIn("passive_os_transport_rollback: false", self.rollback)
        self.assertIn("passive_os_transport_rollback | bool", self.rollback)

    def test_scoped_to_sensor_and_router(self):
        for content in (self.setup, self.rollback):
            self.assertIn("hosts: sensor-01", content)
            self.assertIn("hosts: router-01", content)
            self.assertIn("192.168.2.55", content)
            self.assertIn("192.168.2.1", content)

    def test_source_ip_and_forced_command_restrict_login(self):
        self.assertIn('from="192.168.2.55",restrict,command=', self.setup)
        self.assertIn("/bin/cat /var/lib/homelab-passive-os-outbound/batch.json", self.setup)
        self.assertIn("password_lock: true", self.setup)
        self.assertIn("passive_os_prior_account.rc == 2", self.setup)

    def test_monitoring_and_router_network_not_reconfigured(self):
        for content in (self.setup, self.rollback):
            self.assertNotIn("sshd_config", content)
            self.assertNotIn("systemd:", content)
            self.assertNotIn("nftables", content)
            self.assertNotIn("router-metrics", content)
            self.assertNotIn("router-suricata", content)

    def test_rollback_avoids_spool_and_checks_account(self):
        self.assertIn("Passive OS sanitised file transfer", self.rollback)
        self.assertIn("passive_os_live_pids.rc == 1", self.rollback)
        self.assertNotIn("/var/lib/homelab-passive-os/pending.json", self.rollback)
        self.assertNotIn("/var/log/suricata", self.rollback)


if __name__ == "__main__":
    unittest.main()
