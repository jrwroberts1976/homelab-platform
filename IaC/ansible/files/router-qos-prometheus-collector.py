#!/usr/bin/env python3
"""Read-only CAKE tc collector for node_exporter textfile collector.

Run as root using systemd; output directory must exist and be configured as
node_exporter's textfile collector. No network changes.
"""
import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile

DEVICES = (("upload", "eth1", 13000000), ("download", "ifbqosdl0", 43000000))
FIELDS = {"sent_bytes":"bytes","sent_packets":"packets","dropped":"dropped",
          "overlimits":"overlimits","backlog_bytes":"backlog_bytes",
          "backlog_packets":"backlog_packets"}

def metrics():
    lines = []
    for direction, device, expected in DEVICES:
        p = subprocess.run(["tc", "-s", "qdisc", "show", "dev", device],
                           capture_output=True, text=True, timeout=5)
        if p.returncode:
            raise RuntimeError("cannot inspect " + device)
        text = p.stdout
        if not re.search(r"^qdisc cake\b", text, re.M):
            raise RuntimeError("CAKE missing: " + device)
        label = '{direction="' + direction + '",device="' + device + '"}'
        bandwidth = re.search(r"bandwidth\s+(\d+)([KMG]?)bit\b", text)
        if not bandwidth:
            raise RuntimeError("missing bandwidth: " + device)
        scale = {"":1,"K":1000,"M":1000000,"G":1000000000}[bandwidth.group(2)]
        rate = int(bandwidth.group(1))*scale
        if rate != expected:
            raise RuntimeError("unexpected bandwidth: " + device)
        lines.append("homelab_router_qos_configured_bps" + label + " " + str(rate))
        sent = re.search(r"^ Sent (\d+) bytes (\d+) pkt \(dropped (\d+), overlimits (\d+)", text, re.M)
        backlog = re.search(r"^ backlog (\d+)b (\d+)p", text, re.M)
        if not sent or not backlog:
            raise RuntimeError("missing counters: " + device)
        vals = [int(v) for v in (*sent.groups(),*backlog.groups())]
        for (name, _), val in zip(FIELDS.items(), vals):
            lines.append("homelab_router_qos_" + name + label + " " + str(val))
        for field in ("pk_delay","av_delay","sp_delay"):
            item = re.search(r"^\s*"+field+r"\s+([\d.]+)(us|ms|s)\s*$", text, re.M)
            if item:
                value = float(item.group(1)) * {"us":0.000001,"ms":0.001,"s":1}[item.group(2)]
                lines.append("homelab_router_qos_"+field+"_seconds"+label+" "+str(value))
    lines.append("homelab_router_qos_collection_success 1")
    return "\n".join(lines)+"\n"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",required=True)
    args=parser.parse_args()
    folder=Path(args.output_dir)
    if not folder.is_dir() or folder.is_symlink():
        raise SystemExit("output folder absent or symlink")
    content=metrics()
    fd,path=tempfile.mkstemp(prefix=".qos-",dir=folder)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as out:
            out.write(content)
            out.flush()
            os.fsync(out.fileno())
        os.chmod(path,0o644)
        os.replace(path,folder/"router-qos.prom")
    finally:
        if os.path.exists(path):
            os.unlink(path)

if __name__=="__main__":
    main()
