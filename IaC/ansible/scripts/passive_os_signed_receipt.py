#!/usr/bin/env python3
"""Stage 5.6 OFFLINE receipt attestation prototype; never authorises router ack.

An Ed25519 signature binds a verified local receipt to sanitised wire bytes and
a fresh caller challenge. No SSH, accounts, keys, or checkpoint changes here.
Requires the optional cryptography Python package (fail closed if unavailable).
"""
import base64
import hashlib
import json
import re

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from passive_os_batch_spool import canonical
from passive_os_wire_receiver import validate_wire

RECEIVER_ID = "sensor-01"
NAMESPACE = "homelab-passive-os-receipt-v1"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
RECEIPT_FIELDS = frozenset({"protocol", "batch_id", "digest", "stored_bytes"})
PROOF_FIELDS = frozenset({"protocol", "namespace", "receiver", "batch_id",
                          "digest", "stored_bytes", "wire_sha256", "challenge"})
ENVELOPE_FIELDS = frozenset({"proof", "signature"})
MAX_PROOF_BYTES = 4096


def _record_for(raw):
    batch, canonical_bytes = validate_wire(raw)
    return {
        "protocol": 1, "batch_id": batch["batch_id"],
        "digest": batch["digest"], "stored_bytes": len(canonical_bytes),
    }, canonical_bytes


def _challenge(value):
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise ValueError("Challenge must encode 32 random bytes in lowercase hex")


def _receipt_matches(receipt_bytes, expected):
    if not isinstance(receipt_bytes, bytes) or len(receipt_bytes) > MAX_PROOF_BYTES:
        raise ValueError("Invalid local receipt length")
    try:
        saved = json.loads(receipt_bytes)
    except (UnicodeError, ValueError):
        raise ValueError("Invalid local receipt") from None
    if not isinstance(saved, dict) or set(saved) != RECEIPT_FIELDS or saved != expected:
        raise ValueError("Local receipt does not match wire batch")
    if receipt_bytes != canonical(saved) + b"\n":
        raise ValueError("Local receipt is not canonical")


def attest_locally(wire_bytes, saved_wire_bytes, local_receipt_bytes,
                   challenge, private_key):
    """Test-only attestation over supplied bytes, not a durability guarantee.

    A future signer must read files under a private receiver lock and enforce
    actual storage durability, identity, access controls, and key isolation.
    """
    _challenge(challenge)
    expected, normal = _record_for(wire_bytes)
    if saved_wire_bytes != normal:
        raise ValueError("Saved wire bytes differ")
    _receipt_matches(local_receipt_bytes, expected)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("Ed25519 signing key required")
    proof = {
        "protocol": 1, "namespace": NAMESPACE, "receiver": RECEIVER_ID,
        "batch_id": expected["batch_id"], "digest": expected["digest"],
        "stored_bytes": expected["stored_bytes"],
        "wire_sha256": hashlib.sha256(normal).hexdigest(),
        "challenge": challenge,
    }
    signature = private_key.sign(canonical(proof))
    return canonical({"proof": proof,
                      "signature": base64.b64encode(signature).decode("ascii")}) + b"\n"


def verify_signed_receipt(envelope_bytes, expected_wire_bytes, challenge,
                          pinned_receiver_public_key):
    """Verify pin, signature, batch and nonce; NEVER advance checkpoint."""
    _challenge(challenge)
    if not isinstance(envelope_bytes, bytes) or not 0 < len(envelope_bytes) <= MAX_PROOF_BYTES:
        raise ValueError("Invalid attestation size")
    if not isinstance(pinned_receiver_public_key, Ed25519PublicKey):
        raise ValueError("Pinned Ed25519 verification key required")
    try:
        envelope = json.loads(envelope_bytes)
    except (UnicodeError, ValueError):
        raise ValueError("Invalid attestation JSON") from None
    if not isinstance(envelope, dict) or set(envelope) != ENVELOPE_FIELDS:
        raise ValueError("Invalid attestation envelope")
    proof = envelope["proof"]
    if not isinstance(proof, dict) or set(proof) != PROOF_FIELDS:
        raise ValueError("Invalid attestation proof")
    if envelope_bytes != canonical(envelope) + b"\n":
        raise ValueError("Noncanonical attestation")
    encoded_sig = envelope["signature"]
    if not isinstance(encoded_sig, str) or len(encoded_sig) != 88:
        raise ValueError("Invalid signature length")
    try:
        signature = base64.b64decode(encoded_sig, validate=True)
    except (ValueError, base64.binascii.Error):
        raise ValueError("Invalid signature encoding") from None
    if len(signature) != 64:
        raise ValueError("Invalid Ed25519 signature")
    try:
        pinned_receiver_public_key.verify(signature, canonical(proof))
    except InvalidSignature:
        raise ValueError("Signature verification failed") from None
    expected, normal = _record_for(expected_wire_bytes)
    required = {
        "protocol": 1, "namespace": NAMESPACE, "receiver": RECEIVER_ID,
        "batch_id": expected["batch_id"], "digest": expected["digest"],
        "stored_bytes": expected["stored_bytes"],
        "wire_sha256": hashlib.sha256(normal).hexdigest(),
        "challenge": challenge,
    }
    if proof != required:
        raise ValueError("Attestation does not bind expected batch and challenge")
    return {"status": "signature_verified_only", **expected}
