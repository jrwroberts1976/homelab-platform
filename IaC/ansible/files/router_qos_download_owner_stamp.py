#!/usr/bin/env python3
"""Stamp ownership of a newly-created download IFB.

Not an adoption tool. Caller must be the installer that just created IFB and
must hold the exclusive controller lock. The function refuses a pre-existing
record and verifies kernel alias/index after writing. No cleanup is authorised.
"""
from __future__ import annotations
from pathlib import Path
import secrets
from router_qos_download_owner_record import write_new, load


def stamp_new_ifb(owner_path, boot_id, get_ifindex, get_alias, set_alias, ifb_name="ifbqosdl0"):
    # Caller must have created IFB in this same critical section.
    # A pre-existing record may indicate an interrupted install: fail closed.
    if ifb_name not in ("ifbqosdl0", "ifbqosdl1"):\n        raise ValueError("unapproved IFB name")\n    owner_path = Path(owner_path)
    if owner_path.exists() or owner_path.is_symlink():
        raise FileExistsError("existing or ambiguous ownership record")
    index = get_ifindex()
    if type(index) is not int or index <= 0:
        raise ValueError("unreliable kernel IFB ifindex")
    if get_alias() not in ("", None):
        raise ValueError("IFB already has an alias; refuse adoption")
    token = secrets.token_hex(16)
    alias = "router-qos-download:" + token
    set_alias(alias)
    if get_ifindex() != index or get_alias() != alias:
        raise RuntimeError("kernel identity changed while stamping")
    record = dict(boot_id=boot_id, ifb_name=ifb_name,
                  ifb_ifindex=index, token=token)
    write_new(owner_path, record)
    if load(owner_path) != record:
        raise RuntimeError("ownership record readback mismatch")
    return record


if __name__ == "__main__":
    raise SystemExit("Library-only install primitive; no standalone adoption entrypoint")
