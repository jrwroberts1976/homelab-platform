#!/usr/bin/env python3
"""Narrow edge-01 nftables timestamp fix. No flush, reload or service restart."""
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

CONF = Path("/etc/nftables.conf")
BACKUP = Path("/var/lib/homelab-icmp-edge01/nftables.conf.before")
BASE_SHA = "60dac93ffe0ea440fc4a8941a080b6fb8d2c8655d47baf856e97182a0d1ca29a"
TAG = "homelab-icmp-edge01"
INSERT = "                ip protocol icmp icmp type timestamp-request counter drop comment \"" + TAG + "\"\n"
ANCHOR = "                type filter hook input priority filter;\n"


def run(*args):
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout


def live():
    return run("/usr/sbin/nft", "-a", "list", "chain", "inet", "filter", "input")


def handles(s):
    # nft may canonicalise the implicit IPv4 protocol expression on output.
    result = []
    for line in s.splitlines():
        if 'comment "' + TAG + '"' not in line:
            continue
        rule = re.fullmatch(
            r'\\s*(?:ip protocol icmp )?icmp type timestamp-request '
            r'counter packets \\d+ bytes \\d+ drop comment "'
            + re.escape(TAG) + r'" # handle (\\d+)\\s*',
            line,
        )
        if not rule:
            raise RuntimeError("Unexpected tagged nft rule shape")
        result.append(rule.group(1))
    return result


def validate_identity():
    if Path("/etc/hostname").read_text().strip() != "edge-01":
        raise RuntimeError("Unexpected hostname")
    if "192.168.2.56" not in run("/usr/sbin/ip", "-4", "-o", "addr", "show").split():
        # IP appears as CIDR, so check using a constrained expression.
        if not re.search(r"\binet 192\.168\.2\.56/24\b", run("/usr/sbin/ip", "-4", "-o", "addr", "show")):
            raise RuntimeError("Unexpected IPv4 address")


def atomic_write(path, content):
    fd, name = tempfile.mkstemp(prefix=".icmp-edge01-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(name, 0o644)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main(mode):
    validate_identity()
    original = CONF.read_bytes()
    before = original.decode()
    if before.count(ANCHOR) != 1:
        raise RuntimeError("Expected unique input chain anchor not found")
    expected = before.replace(INSERT, "")
    if hashlib.sha256(expected.encode()).hexdigest() != BASE_SHA:
        raise RuntimeError("Config diverges from audited baseline")
    observed = live()
    count = observed.count("comment \"" + TAG + "\"")
    matching = handles(observed)
    # The audited edge baseline has an empty INPUT chain. Refuse other rules.
    nonstructural = [
        line.strip() for line in observed.splitlines()
        if line.strip() and not line.strip().startswith((
            "table inet filter", "chain input", "type filter hook input", "}"
        ))
    ]
    if len(nonstructural) != len(matching):
        raise RuntimeError("Unexpected INPUT rule or structure; fail closed")
    if len(matching) > 1:
        raise RuntimeError("Ambiguous live tagged rule")
    if mode == "inspect":
        print("CONFIG_TAG_PRESENT=" + str(INSERT in before))
        print("LIVE_TAG_COUNT=" + str(len(matching)))
        return
    if mode == "apply":
        if not BACKUP.exists():
            if INSERT in before or matching:
                raise RuntimeError("Existing rule without owned baseline backup")
            BACKUP.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(BACKUP, original)
        if BACKUP.read_bytes() != expected.encode():
            raise RuntimeError("Backup mismatch")
        if INSERT not in before:
            replacement = before.replace(ANCHOR, ANCHOR + INSERT)
            if replacement.count(INSERT) != 1:
                raise RuntimeError("Non-unique insertion")
            # nft syntax-check a temporary candidate before atomically installing.
            fd, name = tempfile.mkstemp(prefix=".edge-nft-check-", dir="/etc")
            try:
                with os.fdopen(fd, "w") as f:
                    f.write(replacement)
                run("/usr/sbin/nft", "-c", "-f", name)
            finally:
                os.unlink(name)
            atomic_write(CONF, replacement.encode())
            print("CONFIG_ADDED")
        if not matching:
            run("/usr/sbin/nft", "add", "rule", "inet", "filter", "input",
                "ip", "protocol", "icmp", "icmp", "type", "timestamp-request",
                "counter", "drop", "comment", TAG)
            print("RULE_ADDED")
        if len(handles(live())) != 1:
            raise RuntimeError("Rule not found after apply")
    elif mode == "rollback":
        if not BACKUP.exists() or BACKUP.read_bytes() != expected.encode():
            raise RuntimeError("Missing or mismatched original backup")
        if matching:
            run("/usr/sbin/nft", "delete", "rule", "inet", "filter", "input", "handle", matching[0])
            print("RULE_REMOVED")
        if INSERT in before:
            atomic_write(CONF, BACKUP.read_bytes())
            print("CONFIG_RESTORED")
        if handles(live()) or INSERT in CONF.read_text():
            raise RuntimeError("Rollback verification failed")
    else:
        raise RuntimeError("Expected inspect, apply or rollback")


if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) == 2 else "")
    except (OSError, subprocess.CalledProcessError, RuntimeError, UnicodeError) as exc:
        print("EDGE01_ICMP_ERROR=" + str(exc), file=sys.stderr)
        sys.exit(1)
