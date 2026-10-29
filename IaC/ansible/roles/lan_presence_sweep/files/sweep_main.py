"""Run LAN discovery and atomically publish persistent presence data."""

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

from host_identity import (
    attach_verified_hostnames,
    fetch_exporter_interfaces,
    verified_hostnames,
)
from presence_metrics import render_metrics
from presence_state import empty_state, merge_sweep
from sweep_guard import check_population_drop
from sweep_runner import run_discovery


def stage_file(destination, content, mode):
    """Prepare a complete file before replacing the existing one."""
    destination = Path(destination)
    fd, temporary = tempfile.mkstemp(
        prefix=".lan-presence-",
        dir=destination.parent,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary, mode)
        return temporary
    except BaseException:
        os.unlink(temporary)
        raise


def publish(state_path, metrics_path, interface="eth0",
            now=None, get_interfaces=None):
    state_path = Path(state_path)
    metrics_path = Path(metrics_path)

    previous = (
        json.loads(state_path.read_text())
        if state_path.exists() else empty_state()
    )

    observed = run_discovery(interface)
    check_population_drop(previous, observed)

    timestamp = time.time() if now is None else now
    updated = merge_sweep(previous, observed, timestamp)

    fetch = (
        fetch_exporter_interfaces
        if get_interfaces is None else get_interfaces
    )
    try:
        hostnames = verified_hostnames(observed, fetch())
    except (OSError, ValueError) as exc:
        print(
            f"Host identity lookup unavailable: {exc}; "
            "retaining previous identities",
            file=sys.stderr,
        )
        hostnames = {}

    updated = attach_verified_hostnames(
        updated, hostnames, timestamp
    )
    metrics = render_metrics(updated)
    state_json = json.dumps(updated, indent=2, sort_keys=True) + "\n"

    state_tmp = metrics_tmp = None
    try:
        state_tmp = stage_file(state_path, state_json, 0o600)
        metrics_tmp = stage_file(metrics_path, metrics, 0o644)
        os.replace(state_tmp, state_path)
        os.replace(metrics_tmp, metrics_path)
    finally:
        for temporary in (state_tmp, metrics_tmp):
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)

    return len(observed), len(updated["devices"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    parser.add_argument("--metrics", required=True)
    parser.add_argument("--interface", default="eth0")
    args = parser.parse_args()

    online, known = publish(
        args.state, args.metrics, args.interface
    )
    print(f"LAN sweep published: {online} observed, {known} known")
