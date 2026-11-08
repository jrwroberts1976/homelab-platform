#!/usr/bin/env python3
"""One-shot best-effort OS sample from the TAIL of existing Suricata EVE.

No service changes, background timer, log rotation manipulation, checkpoint,
or EVE export. Writes *only* a bounded minimal wire JSON batch that an already
restricted SSH key can read. Designed for a manual KISS homelab pilot.
"""
import argparse
import hashlib
import json
import os
import stat
import tempfile
from pathlib import Path

from router_eve_minimizer import minimize
from passive_os_batch_spool import canonical, digest
from passive_os_ssh_export import MAX_WIRE_BYTES

READ_BYTES = 1024 * 1024
MAX_EVENTS = 2000
MAX_LINE = 8192
DEFAULT_EVE = Path("/var/log/suricata/eve.json")
DEFAULT_OUT = Path("/var/lib/homelab-passive-os-outbound/batch.json")


def sample_tail(path, read_bytes=READ_BYTES):
    """Skip the first truncated line when tailing; skip oversized lines."""
    if not 0 < read_bytes <= READ_BYTES:
        raise ValueError("Invalid read ceiling")
    with path.open("rb") as fh:
        info = os.fstat(fh.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("EVE source must be regular")
        start = max(0, info.st_size - read_bytes)
        fh.seek(start)
        if start:
            fh.readline(MAX_LINE + 1)  # discard possibly incomplete first record
        sample = fh.read(read_bytes)
    observations = []
    for line in sample.splitlines():
        if len(observations) >= MAX_EVENTS:
            break
        if not line or len(line) > MAX_LINE:
            continue
        try:
            observation = minimize(json.loads(line))
        except (UnicodeError, ValueError, TypeError):
            continue
        if observation is not None:
            observations.append(observation)
    return observations


def make_wire(observations):
    """Digest only minimised evidence; never include UA, domains or URLs."""
    clean = canonical(observations)
    wire = {
        "protocol": 1,
        "batch_id": hashlib.sha256(b"passive-os-tail-v1:" + clean).hexdigest(),
        "digest": digest(clean),
        "observations": observations,
    }
    output = canonical(wire) + b"\n"
    if len(output) > MAX_WIRE_BYTES:
        raise ValueError("Output exceeds transfer limit")
    return output


def publish_tail(eve, output, group_id):
    if os.geteuid() != 0:
        raise PermissionError("Root required to publish")
    if output.is_symlink():
        raise ValueError("Output symlink refused")
    parent = output.parent
    info = parent.stat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or (
        stat.S_IMODE(info.st_mode) != 0o750 or info.st_gid != group_id
    ):
        raise ValueError("Unexpected outbound directory owner/group/mode")
    wire = make_wire(sample_tail(eve))
    fd, temp_name = tempfile.mkstemp(prefix=".passive-os-", dir=parent)
    try:
        os.fchmod(fd, 0o640)
        os.fchown(fd, 0, group_id)
        with os.fdopen(fd, "wb") as out:
            out.write(wire)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temp_name, output)
        dfd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return json.loads(wire)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--eve", type=Path, default=DEFAULT_EVE)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--group", default="homelab-os-transfer")
    args = ap.parse_args()
    import grp
    group_id = grp.getgrnam(args.group).gr_gid
    wire = publish_tail(args.eve, args.output, group_id)
    print(json.dumps({"batch_id": wire["batch_id"],
                      "observations": len(wire["observations"]),
                      "status": "published-sanitised-tail-sample"}, sort_keys=True))


if __name__ == "__main__":
    main()
