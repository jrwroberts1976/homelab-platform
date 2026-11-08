#!/usr/bin/env python3
"""Stage 5.7G: synthetic, local-only end-to-end passive OS receipt tests.

No SSH, network access, production paths, source acknowledgement, or timers.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from passive_os_batch_spool import prepare, validated_pending
from passive_os_ssh_export import export_batch
from passive_os_offline_receipt_coordinator import receive_and_attest_local
from passive_os_signed_receipt import verify_signed_receipt

CHALLENGE = "a4" * 32
OTHER_CHALLENGE = "b7" * 32


class OfflineEndToEndTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.eve = self.root / "synthetic-eve.json"
        self.spool = self.root / "spool"
        self.destination = self.root / "receiver"
        self.destination.mkdir(mode=0o700)
        self.signer = Ed25519PrivateKey.generate()
        self.eve.write_text(json.dumps({
            "timestamp": "2026-11-06T12:00:00Z",
            "src_ip": "192.168.2.113",
            "event_type": "http",
            "http": {"http_user_agent": "Mozilla/5.0 (X11; CrOS x86_64 1)",
                     "url": "/private-path"}
        }) + "\n", encoding="utf-8")
        result = prepare(self.eve, self.spool)
        self.assertEqual(result["status"], "prepared")
        self.pending_id = result["batch_id"]
        self.wire = export_batch(self.spool / "pending.json", "get-batch")

    def deliver(self, wire=None, challenge=CHALLENGE, signer=None):
        return receive_and_attest_local(
            self.wire if wire is None else wire,
            self.destination, challenge, self.signer if signer is None else signer,
            synthetic_test_only=True,
        )

    def assert_source_unchanged(self):
        pending = validated_pending(self.spool / "pending.json")
        self.assertIsNotNone(pending)
        self.assertEqual(pending["batch_id"], self.pending_id)
        self.assertFalse((self.spool / "checkpoint.json").exists())

    def test_full_synthetic_pipeline_signature_and_privacy(self):
        self.assertNotIn(b"/private-path", self.wire)
        self.assertNotIn(b"http_user_agent", self.wire)
        result = self.deliver()
        self.assertEqual(result["store_status"], "stored")
        self.assertEqual(result["verification_status"], "signature_verified_only")
        self.assertEqual(result["batch_id"], self.pending_id)
        verification = verify_signed_receipt(
            result["envelope"], self.wire, CHALLENGE, self.signer.public_key())
        self.assertEqual(verification["status"], "signature_verified_only")
        self.assert_source_unchanged()

    def test_retry_is_idempotent_and_does_not_acknowledge(self):
        first = self.deliver()
        retry = self.deliver()
        self.assertEqual(retry["store_status"], "duplicate")
        self.assertEqual(first["envelope"], retry["envelope"])
        self.assertEqual(prepare(self.eve, self.spool)["status"], "pending")
        self.assert_source_unchanged()

    def test_wrong_key_and_challenge_reject_existing_proof(self):
        envelope = self.deliver()["envelope"]
        with self.assertRaises(ValueError):
            verify_signed_receipt(envelope, self.wire, OTHER_CHALLENGE,
                                  self.signer.public_key())
        with self.assertRaises(ValueError):
            verify_signed_receipt(envelope, self.wire, CHALLENGE,
                                  Ed25519PrivateKey.generate().public_key())
        self.assert_source_unchanged()

    def test_corrupt_delivery_does_not_advance_source(self):
        corrupt = self.wire.replace(b"ChromeOS", b"Android")
        self.assertNotEqual(corrupt, self.wire)
        with self.assertRaises(ValueError):
            self.deliver(wire=corrupt)
        self.assertEqual(list(self.destination.iterdir()), [])
        self.assert_source_unchanged()

    def test_receipt_file_tampering_is_rejected(self):
        result = self.deliver()
        receipt = self.destination / (result["batch_id"] + ".receipt.json")
        receipt.write_bytes(b"{}\n")
        with self.assertRaises(ValueError):
            self.deliver()
        self.assert_source_unchanged()


if __name__ == "__main__":
    unittest.main()
