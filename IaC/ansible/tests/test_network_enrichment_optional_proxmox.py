#!/usr/bin/env python3
"""Offline regression tests for the production enricher's optional guest mapping.

Extract and execute the actual function from the Jinja2 Python template,
without running its global Nmap/scanning code or requiring Ansible/Jinja.
"""
import ast
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

TEMPLATE = (
    Path(__file__).resolve().parents[1]
    / "roles/network_host_enrichment/templates/"
    "homelab-network-host-enricher.py.j2"
)
SOURCE = TEMPLATE.read_text()
START = SOURCE.index("def selected_proxmox_identity_by_mac(inventory):")
END = SOURCE.index("\ndef prom_escape(value):", START)
FUNCTION = SOURCE[START:END]
CODE = compile(FUNCTION, str(TEMPLATE), "exec")


class OptionalGuestIdentityTests(unittest.TestCase):
    def call(self, source, loader):
        fake = types.ModuleType("proxmox_guest_identity")
        fake.load_snapshot = loader
        scope = {
            "PROXMOX_SOURCE": source,
            "PROXMOX_HELPER_DIR": Path("/nonexistent"),
            "PROXMOX_SNAPSHOT_FILE": Path("/nonexistent/snapshot.json"),
            "PROXMOX_MAX_AGE": 172800,
            "sys": sys,
            "json": json,
            "os": __import__("os"),
        }
        exec(CODE, scope)
        with patch.dict(sys.modules, {"proxmox_guest_identity": fake}):
            return scope["selected_proxmox_identity_by_mac"]({})

    def test_valid_optional_identity_is_used(self):
        value = {"aa:bb:cc:dd:ee:ff": {"vmid": "100"}}
        result, counts = self.call(
            "snapshot_optional",
            lambda *_args, **_kwargs: (value, {"matched_guest_macs": 1}),
        )
        self.assertEqual(result, value)
        self.assertEqual(counts["matched_guest_macs"], 1)

    def test_optional_identity_fails_closed_for_stale_snapshot(self):
        def stale(*_args, **_kwargs):
            raise ValueError("stale snapshot")
        result, counts = self.call("snapshot_optional", stale)
        self.assertEqual(result, {})
        self.assertEqual(counts, {"snapshot_valid": False})

    def test_optional_identity_fails_closed_for_missing_file(self):
        def missing(*_args, **_kwargs):
            raise FileNotFoundError("missing")
        result, counts = self.call("snapshot_optional", missing)
        self.assertEqual(result, {})
        self.assertEqual(counts, {"snapshot_valid": False})

    def test_strict_source_still_refuses_stale_snapshot(self):
        def stale(*_args, **_kwargs):
            raise ValueError("stale snapshot")
        with self.assertRaises(ValueError):
            self.call("snapshot", stale)

    def test_offline_guest_identity_is_not_carried_when_unavailable(self):
        self.assertIn(
            'if proxmox_identity_available and "proxmox" in prior:',
            SOURCE,
        )
        self.assertIn('"proxmox": proxmox_by_mac.get(mac)', SOURCE)
        self.assertIn(
            '"homelab_network_host_enrichment_proxmox_identity_available "',
            SOURCE,
        )


if __name__ == "__main__":
    unittest.main()
