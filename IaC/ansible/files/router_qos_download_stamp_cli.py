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
from router_qos_download_owner_record import load

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

def release_after_delete():
    """Forget the record only after this install's IFB has been removed.

    This is metadata cleanup, not permission to delete an interface.
    A missing/ambiguous interface check fails closed.
    """
    import os
    import stat
    owner = Path(OWNER)
    record = load(owner)
    boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    if record["boot_id"] != boot:
        raise RuntimeError("ownership boot changed")
    result = subprocess.run(["ip", "link", "show", "dev", IFB],
                            capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        raise RuntimeError("IFB still exists; ownership record preserved")
    if result.returncode != 1:
        raise RuntimeError("cannot establish IFB absence")
    fd = os.open(owner, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        st = os.fstat(fd)
        pst = os.lstat(owner)
        if not stat.S_ISREG(st.st_mode) or (st.st_dev, st.st_ino) != (pst.st_dev, pst.st_ino):
            raise RuntimeError("ownership record changed during verification")
        if load(owner) != record:
            raise RuntimeError("ownership record changed")
        if (os.lstat(owner).st_dev, os.lstat(owner).st_ino) != (st.st_dev, st.st_ino):
            raise RuntimeError("ownership file replaced")
        owner.unlink()
    finally:
        os.close(fd)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("stamp", "release-after-delete") or __import__("os").geteuid() != 0:
        raise SystemExit("REFUSE: root-only stamp/release operation")
    if sys.argv[1] == "release-after-delete":
        release_after_delete()
        print("PASS: removed IFB ownership record released")
    else:
        boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        stamp_new_ifb(OWNER, boot, ifindex, alias, set_alias)
        print("PASS: newly created IFB ownership stamped")

if __name__ == "__main__":
    main()
