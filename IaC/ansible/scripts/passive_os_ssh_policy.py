#!/usr/bin/env python3
"""OFFLINE security policy helper for future passive-OS SSH transport.

Does not generate credentials, modify authorized_keys, open connections, or
deploy a forced-command program. Values are constants for review, not an
authorised production configuration.
"""
import base64
import ipaddress
import re

ROUTER_IP = "192.168.2.1"
SENSOR_IP = "192.168.2.55"
FORCED_COMMAND = "/usr/local/libexec/homelab-passive-os-export"
KEY_TYPES = frozenset({"ssh-ed25519"})
KEY_B64 = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")
MAX_KEY_TEXT = 2048


def validate_public_key(key):
    """Accept one standalone Ed25519 OpenSSH public key, never key options."""
    if not isinstance(key, str) or len(key) > MAX_KEY_TEXT:
        raise ValueError("Invalid public key input")
    if "\n" in key or "\r" in key or "\x00" in key:
        raise ValueError("Multiple lines or control characters forbidden")
    pieces = key.strip().split()
    if len(pieces) not in (2, 3) or pieces[0] not in KEY_TYPES:
        raise ValueError("Only a single Ed25519 public key is allowed")
    encoded = pieces[1]
    if not KEY_B64.fullmatch(encoded):
        raise ValueError("Invalid public key encoding")
    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (ValueError, base64.binascii.Error):
        raise ValueError("Invalid public key base64") from None
    # SSH wire format: four-byte length, then b"ssh-ed25519".
    if len(decoded) < 4 or len(decoded) > 256:
        raise ValueError("Unexpected public key size")
    name_size = int.from_bytes(decoded[:4], "big")
    if name_size != len(b"ssh-ed25519") or decoded[4:4 + name_size] != b"ssh-ed25519":
        raise ValueError("Public key type mismatch")
    return " ".join(pieces[:2])


def authorized_key_line(key, source_ip=SENSOR_IP):
    """Build a candidate key policy; never install or authorize it."""
    try:
        addr = ipaddress.ip_address(source_ip)
    except (TypeError, ValueError):
        raise ValueError("Invalid source address") from None
    if str(addr) != SENSOR_IP:
        raise ValueError("Source must be the approved sensor-01 IP")
    validated = validate_public_key(key)
    options = (
        'restrict',
        'from="' + SENSOR_IP + '"',
        'command="' + FORCED_COMMAND + '"',
    )
    return ",".join(options) + " " + validated


def ssh_client_options(known_hosts, identity):
    """Return fixed client options for a future, manually reviewed invocation.

    Paths must be trusted, absolute, and not injected into a shell command.
    This only constructs an argv list, never executes ssh.
    """
    for name, path in (("known_hosts", known_hosts), ("identity", identity)):
        if not isinstance(path, str) or not path.startswith("/") or "\x00" in path:
            raise ValueError("Unsafe " + name + " path")
        if "\n" in path or "\r" in path or len(path) > 512:
            raise ValueError("Unsafe " + name + " path")
    return [
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=yes",
        "-o", "UserKnownHostsFile=" + known_hosts,
        "-o", "IdentitiesOnly=yes",
        "-o", "PasswordAuthentication=no",
        "-o", "KbdInteractiveAuthentication=no",
        "-o", "ForwardAgent=no",
        "-o", "ClearAllForwardings=yes",
        "-o", "RequestTTY=no",
        "-o", "ConnectTimeout=3",
        "-o", "ConnectionAttempts=1",
        "-i", identity,
    ]
