"""Publish MAC-keyed device metrics without initiating scans."""

import argparse
import json
import os
import tempfile
import time
from pathlib import Path

from device_metrics import render_metrics
from mac_vendors import load_vendors
from worker_state import load_state


def publish(collector_path, profiles_path, output_path,
            now=None, vendors_path=None):
    collector = json.loads(Path(collector_path).read_text())
    profiles = load_state(profiles_path)

    # Validate all source data before touching the published metrics.
    vendors = load_vendors(vendors_path) if vendors_path else {}
    metrics = render_metrics(collector, profiles, vendors=vendors)

    timestamp = int(time.time() if now is None else now)
    metrics += (
        "# HELP homelab_router_device_metrics_generated_timestamp_seconds "
        "Last successful device metrics publication.\n"
        "# TYPE homelab_router_device_metrics_generated_timestamp_seconds gauge\n"
        f"homelab_router_device_metrics_generated_timestamp_seconds {timestamp}\n"
    )

    output = Path(output_path)
    if output.name != "homelab_router_devices.prom":
        raise ValueError("Unexpected metrics output filename")
    if not output.parent.is_dir():
        raise FileNotFoundError(output.parent)

    fd, temporary = tempfile.mkstemp(
        prefix=".homelab_router_devices.",
        suffix=".tmp",
        dir=output.parent,
    )
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(metrics)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

    return len(collector["devices"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collector", required=True)
    parser.add_argument("--profiles", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--vendors", required=True)
    args = parser.parse_args()

    count = publish(
        args.collector, args.profiles, args.output,
        vendors_path=args.vendors,
    )
    print(f"Published metrics for {count} devices", flush=True)


if __name__ == "__main__":
    main()
