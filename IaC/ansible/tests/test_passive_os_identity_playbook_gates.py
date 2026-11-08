#!/usr/bin/env python3
"""Offline source-level guardrails for dormant SSH identity Ansible playbooks.

These checks are deliberately conservative; a passing test is NOT a security
proof and does not authorize running either playbook on router-01.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "playbooks"


class IdentityPlaybookGatesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.provision = (ROOT / "passive-os-ssh-identity-provision-gated.yml").read_text()
        cls.rollback = (ROOT / "passive-os-ssh-identity-rollback-gated.yml").read_text()

    def test_provision_default_denies(self):
        self.assertIn("passive_os_approved: false", self.provision)
        self.assertIn("passive_os_fingerprint_independently_verified: false", self.provision)
        self.assertIn("passive_os_approved_fingerprint: ''", self.provision)

    def test_provision_requires_canonical_target(self):
        self.assertIn("hosts: router-01", self.provision)
        self.assertIn("ansible_host == '192.168.2.1'", self.provision)
        self.assertIn("runtime_hostname.stdout == 'raspberrypi'", self.provision)

    def test_provision_has_no_transport_activation(self):
        self.assertIn("password_lock: true", self.provision)
        self.assertIn("shell: /usr/sbin/nologin", self.provision)
        self.assertIn("create_home: false", self.provision)
        self.assertNotIn("ansible.posix.authorized_key:", self.provision)
        self.assertNotIn("ansible.builtin.service:", self.provision)
        self.assertNotIn("ansible.builtin.systemd:", self.provision)

    def test_provision_refuses_existing_identity(self):
        self.assertIn("existing_transfer_user.rc == 2", self.provision)

    def test_rollback_default_denies(self):
        self.assertIn("passive_os_rollback_approved: false", self.rollback)
        self.assertIn("passive_os_rollback_approved | bool", self.rollback)

    def test_rollback_checks_account_ownership_and_activity(self):
        self.assertIn("passive_rollback_passwd.stdout.split(':')[4]", self.rollback)
        self.assertIn("passive_rollback_passwd.stdout.split(':')[5]", self.rollback)
        self.assertIn("passive_rollback_passwd.stdout.split(':')[6]", self.rollback)
        self.assertIn("passive_rollback_processes.rc == 1", self.rollback)
        self.assertIn("passive_rollback_authorized_keys.stat.exists", self.rollback)

    def test_rollback_does_not_touch_home_or_services(self):
        self.assertIn("remove: false", self.rollback)
        self.assertNotIn("ansible.builtin.service:", self.rollback)
        self.assertNotIn("ansible.builtin.systemd:", self.rollback)
        self.assertNotIn("ansible.posix.authorized_key:", self.rollback)


if __name__ == "__main__":
    unittest.main()
