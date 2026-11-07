#!/usr/bin/env python3
"""Synthetic cryptographic receipt tests, with disposable in-memory keys."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(ROOT))
from passive_os_batch_spool import canonical, prepare
from passive_os_ssh_export import export_batch
from passive_os_wire_receiver import receive_wire
from passive_os_signed_receipt import attest_locally, verify_signed_receipt

CHALLENGE = "a1" * 32
OTHER_CHALLENGE = "b2" * 32


class SignedReceiptTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        eve = root / "synthetic-eve.json"
        self.spool = root / "spool"
        self.dest = root / "receiver"
        eve.write_text(json.dumps({
            "timestamp": "2026-11-06T12:00:00Z",
            "src_ip": "192.168.2.113",
            "event_type": "http",
            "http": {"http_user_agent": "CrOS 123"},
        }) + "\n")
        prepare(eve, self.spool)
        self.wire = export_batch(self.spool / "pending.json", "get-batch")
        receipt = receive_wire(self.wire, self.dest)
        self.saved = (self.dest / (receipt["batch_id"] + ".json")).read_bytes()
        self.local_receipt = (
            self.dest / (receipt["batch_id"] + ".receipt.json")
        ).read_bytes()
        self.key = Ed25519PrivateKey.generate()
        self.pin = self.key.public_key()

    def signed(self, challenge=CHALLENGE):
        return attest_locally(self.wire, self.saved, self.local_receipt,
                              challenge, self.key)

    def test_valid_signature_binds_batch_and_challenge(self):
        result = verify_signed_receipt(self.signed(), self.wire, CHALLENGE, self.pin)
        self.assertEqual(result["status"], "signature_verified_only")

    def test_wrong_receiver_key_fails(self):
        wrong_pin = Ed25519PrivateKey.generate().public_key()
        with self.assertRaisesRegex(ValueError, "Signature verification failed"):
            verify_signed_receipt(self.signed(), self.wire, CHALLENGE, wrong_pin)

    def test_stale_challenge_cannot_replay(self):
        with self.assertRaisesRegex(ValueError, "challenge"):
            verify_signed_receipt(self.signed(), self.wire, OTHER_CHALLENGE, self.pin)

    def test_modified_signature_fails(self):
        obj = json.loads(self.signed())
        sig = obj["signature"]
        obj["signature"] = ("A" if sig[0] != "A" else "B") + sig[1:]
        with self.assertRaisesRegex(ValueError, "Signature verification failed"):
            verify_signed_receipt(canonical(obj) + b"\n", self.wire, CHALLENGE, self.pin)

    def test_modified_authenticated_proof_fails(self):
        obj = json.loads(self.signed())
        obj["proof"]["receiver"] = "router-01"
        with self.assertRaisesRegex(ValueError, "Signature verification failed"):
            verify_signed_receipt(canonical(obj) + b"\n", self.wire, CHALLENGE, self.pin)

    def test_missing_local_receipt_rejected(self):
        with self.assertRaises(ValueError):
            attest_locally(self.wire, self.saved, b"", CHALLENGE, self.key)

    def test_saved_batch_corruption_rejected(self):
        with self.assertRaisesRegex(ValueError, "Saved wire bytes differ"):
            attest_locally(self.wire, b"corrupt", self.local_receipt,
                           CHALLENGE, self.key)

    def test_modified_local_receipt_rejected(self):
        record = json.loads(self.local_receipt)
        record["stored_bytes"] += 1
        with self.assertRaisesRegex(ValueError, "Local receipt does not match"):
            attest_locally(self.wire, self.saved, canonical(record) + b"\n",
                           CHALLENGE, self.key)

    def test_mismatched_expected_wire_rejected(self):
        obj = json.loads(self.wire)
        obj["batch_id"] = "f" * 64
        different_wire = canonical(obj) + b"\n"
        with self.assertRaisesRegex(ValueError, "does not bind expected"):
            verify_signed_receipt(self.signed(), different_wire, CHALLENGE, self.pin)

    def test_invalid_challenge_rejected(self):
        with self.assertRaisesRegex(ValueError, "Challenge"):
            self.signed("attacker-chosen-short-value")

    def test_receiver_proof_does_not_ack_checkpoint(self):
        result = verify_signed_receipt(self.signed(), self.wire, CHALLENGE, self.pin)
        self.assertEqual(result["status"], "signature_verified_only")
        self.assertTrue((self.spool / "pending.json").exists())
        self.assertFalse((self.spool / "checkpoint.json").exists())


if __name__ == "__main__":
    unittest.main()
