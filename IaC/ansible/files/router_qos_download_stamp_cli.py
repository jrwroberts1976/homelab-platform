#!/usr/bin/env python3
"""Install-only owner stamp CLI for newly created IFB.

Must be called under the controller flock immediately after successful ip link
add. No adoption and no deletion. Existing /run record causes refusal.
"""
import json
from pathlib import Path
import subprocess
import sys
from router_qos_download_owner_stamp import stamp_new_ifb

OWNER = "/run/router-qos-download-basic.owner.json"
IFB = "ifbqosdl0"

def run(*args):
    return subprocess.check_output(args, text=True, timeout=5).strip()

def ifindex():
    return int(Path(f"/sys/class/net/{IFB}/ifindex").read_text().strip())

def alias():
    data = json.loads(run("ip", "-j", "link", "show", "dev", IFB))
    if len(data) != 1 or data[0].get("ifname") != IFB:
        raise RuntimeError("IFB identity ambiguous")
    return data[0].get("ifalias", "")

def set_alias(value):
    subprocess.run(["ip", "link", "set", "dev", IFB, "alias", value],
                   check=True, timeout=5)

def main():
    if len(sys.argv) != 2 or sys.argv[1] != "stamp" or __import__("os").geteuid() != 0:
        raise SystemExit("REFUSE: root-only install stamp")
    boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    stamp_new_ifb(OWNER, boot, ifindex, alias, set_alias)
    print("PASS: newly created IFB ownership stamped")

if __name__ == "__main__":
    main()
