#!/usr/bin/env python3
"""OFFLINE transport plan for restricted passive-OS SSH retrieval.

Builds a fixed argv. Does NOT execute ssh, trust a host key, create keys, or
ack a batch. Candidate only; remote account has not been activated.
"""
from passive_os_ssh_policy import ROUTER_IP, ssh_client_options

REMOTE_ACCOUNT = "homelab-os-transfer"
KNOWN_HOSTS = "/etc/homelab-passive-os/known_hosts"
IDENTITY = "/etc/homelab-passive-os/id_ed25519"
REMOTE_REQUEST = "get-batch"
MAX_WIRE_BYTES = 2 * 1024 * 1024 + 8192


def retrieval_argv():
    """Produce exactly one read-only SSH request, with no caller-supplied args."""
    options = ssh_client_options(KNOWN_HOSTS, IDENTITY)
    return ["ssh", *options, "-T", "--",
            REMOTE_ACCOUNT + "@" + ROUTER_IP, REMOTE_REQUEST]


def validate_retrieved_stdout(stdout, returncode, stderr=b""):
    """Fail closed on missing/truncated/excessive or unsuccessful remote output.

    Never parse stderr as data; never accept a failed SSH command's stdout.
    This function only validates the response; it never stores or acknowledges.
    """
    if type(returncode) is not int or returncode != 0:
        raise ValueError("SSH retrieval failed")
    if not isinstance(stdout, bytes) or not 0 < len(stdout) <= MAX_WIRE_BYTES:
        raise ValueError("Invalid SSH response size")
    if not isinstance(stderr, bytes) or len(stderr) > 8192:
        raise ValueError("Unexpected SSH diagnostic length")
    from passive_os_wire_receiver import validate_wire
    wire, canonical_bytes = validate_wire(stdout)
    if stdout != canonical_bytes:
        raise ValueError("Noncanonical SSH response")
    return wire
