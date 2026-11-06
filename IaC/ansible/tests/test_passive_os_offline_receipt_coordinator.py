#!/usr/bin/env python3
"""Stage 5.7F synthetic local locked receipt tests. No real network."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from passive_os_batch_spool import prepare
from passive_os_ssh_export import export_batch
from passive_os_offline_receipt_coordinator import receive_and_attest_local
from passive_os_signed_receipt import verify_signed_receipt

CHALLENGE = "ca" * 32
NEW_CHALLENGE = "db" * 32


class OfflineReceiptCoordinatorTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.spool = self.root / "spool"
        self.dest = self.root / "receiver"
        self.dest.mkdir(mode=0o700)
        eve = self.root / "eve.json"
        eve.write_text(json.dumps({
            "timestamp": "2026-11-06T12:00:00Z",
            "src_ip": "192.168.2.113", "event_type": "http",
            "http": {"http_user_agent": "CrOS 123"}
        }) + "\n")
        prepare(eve, self.spool)
        self.wire = export_batch(self.spool / "pending.json", "get-batch")
        self.key = Ed25519PrivateKey.generate()

    def call(self, **kwargs):
        return receive_and_attest_local(self.wire, self.dest, CHALLENGE,
                                        self.key, synthetic_test_only=True,
                                        **kwargs)

    def test_successfully_stores_and_signs(self):
        result = self.call()
        self.assertEqual(result["store_status"], "stored")
        self.assertEqual(result["verification_status"], "signature_verified_only")
        self.assertEqual(verify_signed_receipt(
            result["envelope"], self.wire, CHALLENGE, self.key.public_key()
        )["status"], "signature_verified_only")

    def test_duplicate_delivery_keeps_durable_receipt(self):
        first = self.call()
        second = self.call()
        self.assertEqual(second["store_status"], "duplicate")
        self.assertEqual(first["envelope"], second["envelope"])

    def test_new_challenge_invalidates_old_envelope(self):
        old = self.call()
        with self.assertRaisesRegex(ValueError, "challenge"):
            verify_signed_receipt(old["envelope"], self.wire,
                                  NEW_CHALLENGE, self.key.public_key())

    def test_different_verification_key_refuses(self):
        result = self.call()
        with self.assertRaisesRegex(ValueError, "Signature verification failed"):
            verify_signed_receipt(result["envelope"], self.wire, CHALLENGE,
                                  Ed25519PrivateKey.generate().public_key())

    def test_missing_synthetic_gate_refused(self):
        with self.assertRaises(PermissionError):
            receive_and_attest_local(self.wire, self.dest, CHALLENGE, self.key)
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_untrusted_destination_mode_refused(self):
        self.dest.chmod(0o755)
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            self.call()
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_symlink_lock_refused(self):
        target = self.root / "target"
        target.write_text("do not touch")
        (self.dest / ".lock").symlink_to(target)
        with self.assertRaisesRegex(ValueError, "Symlinked lock"):
            self.call()
        self.assertEqual(target.read_text(), "do not touch")

    def test_invalid_wire_does_not_create_receipt(self):
        with self.assertRaises(ValueError):
            receive_and_attest_local(self.wire[:17], self.dest, CHALLENGE,
                                     self.key, synthetic_test_only=True)
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_wrong_challenge_rejected_without_store(self):
        with self.assertRaisesRegex(ValueError, "Challenge"):
            receive_and_attest_local(self.wire, self.dest, "short",
                                     self.key, synthetic_test_only=True)
        self.assertFalse(any(self.dest.glob("*.receipt.json")))

    def test_pending_source_never_acknowledged(self):
        self.call()
        self.assertTrue((self.spool / "pending.json").exists())
        self.assertFalse((self.spool / "checkpoint.json").exists())


if __name__ == "__main__":
    unittest.main()
