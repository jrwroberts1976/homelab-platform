#!/usr/bin/env python3
"""Read-only Suricata NFQUEUE metrics for node_exporter textfile."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile

QUEUE_PATH = Path("/proc/net/netfilter/nfnetlink_queue")
OUTPUT_NAME = "router-ips.prom"

def command(*args):
    return subprocess.run(
        args, capture_output=True, text=True, timeout=5
    )

def metrics():
    lines = []

    table = command("nft", "list", "table", "inet", "router_suricata_ips")
    active = int(table.returncode == 0)

    service = command(
        "systemctl", "is-active", "--quiet",
        "router-suricata-nfq.service"
    )
    inspector = int(service.returncode == 0)

    lines.append(f"homelab_router_ips_active {active}")
    lines.append(f"homelab_router_ips_inspector_up {inspector}")

    queues = []

    if QUEUE_PATH.exists():
        for row in QUEUE_PATH.read_text().splitlines():
            fields = row.split()
            if len(fields) >= 8 and fields[0] == "10":
                queues.append(fields)

    lines.append(f"homelab_router_ips_queue_registered {int(bool(queues))}")

    if queues:
        # Kernel format:
        # queue_num peer_portid queue_total copy_mode copy_range
        # queue_dropped user_dropped id_sequence
        fields = queues[0]

        values = {
            "queue_depth": int(fields[2]),
            "queue_dropped_total": int(fields[5]),
            "queue_user_dropped_total": int(fields[6]),
            "queue_packet_id": int(fields[7]),
        }

        for name, value in values.items():
            lines.append(f"homelab_router_ips_{name} {value}")

    lines.append("homelab_router_ips_collection_success 1")
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    folder = Path(args.output_dir)

    if not folder.is_dir() or folder.is_symlink():
        raise SystemExit("Invalid output directory")

    content = metrics()

    fd, temporary = tempfile.mkstemp(prefix=".ips-", dir=folder)

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())

        os.chmod(temporary, 0o644)
        os.replace(temporary, folder / OUTPUT_NAME)

    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

if __name__ == "__main__":
    main()
