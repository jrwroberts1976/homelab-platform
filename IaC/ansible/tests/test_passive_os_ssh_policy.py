#!/usr/bin/env python3
"""Policy-only tests: no SSH access, keys written, or privileged changes."""
import base64
import importlib.util
import pathlib
import struct
import unittest

FILE = pathlib.Path(__file__).resolve().parents[1] / "scripts/passive_os_ssh_policy.py"
spec = importlib.util.spec_from_file_location("passive_os_ssh_policy", FILE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def example_key():
    # Synthetic OpenSSH-format key; not a valid authentication credential.
    def field(value):
        return struct.pack(">I", len(value)) + value
    wire = field(b"ssh-ed25519") + field(b"\x00" * 32)
    return "ssh-ed25519 " + base64.b64encode(wire).decode("ascii")


class PolicyTests(unittest.TestCase):
    def test_candidate_line_has_restrict_source_and_fixed_command(self):
        line = m.authorized_key_line(example_key())
        self.assertTrue(line.startswith(
            'restrict,from="192.168.2.55",command="/usr/local/libexec/homelab-passive-os-export" '
        ))
        self.assertTrue(line.endswith(example_key()))

    def test_wrong_source_ip_rejected(self):
        with self.assertRaises(ValueError):
            m.authorized_key_line(example_key(), "192.168.2.56")

    def test_source_injection_rejected(self):
        with self.assertRaises(ValueError):
            m.authorized_key_line(example_key(), '192.168.2.55",command="sh')

    def test_no_rsa_or_other_key_types(self):
        with self.assertRaises(ValueError):
            m.validate_public_key("ssh-rsa AAAA")

    def test_no_embedded_key_options(self):
        with self.assertRaises(ValueError):
            m.validate_public_key('command="sh" ' + example_key())

    def test_no_multiline_keys(self):
        with self.assertRaises(ValueError):
            m.validate_public_key(example_key() + "\n" + example_key())

    def test_invalid_base64_rejected(self):
        with self.assertRaises(ValueError):
            m.validate_public_key("ssh-ed25519 not.valid")

    def test_mismatched_wire_key_type_rejected(self):
        wire = struct.pack(">I", 7) + b"ssh-rsa" + b"\x00" * 40
        bad = "ssh-ed25519 " + base64.b64encode(wire).decode()
        with self.assertRaises(ValueError):
            m.validate_public_key(bad)

    def test_client_host_key_checking_cannot_be_disabled(self):
        options = m.ssh_client_options(
            "/etc/homelab-passive-os/known_hosts",
            "/etc/homelab-passive-os/id_ed25519",
        )
        self.assertIn("StrictHostKeyChecking=yes", options)
        self.assertIn("BatchMode=yes", options)
        self.assertIn("IdentitiesOnly=yes", options)
        self.assertIn("ClearAllForwardings=yes", options)
        self.assertIn("ForwardAgent=no", options)
        self.assertIn("RequestTTY=no", options)

    def test_relative_ssh_path_rejected(self):
        with self.assertRaises(ValueError):
            m.ssh_client_options("known_hosts", "/secure/key")

    def test_newline_in_path_rejected(self):
        with self.assertRaises(ValueError):
            m.ssh_client_options("/secure/known_hosts\nextra", "/secure/key")


if __name__ == "__main__":
    unittest.main()
