#!/usr/bin/env python3
"""Offline mocked Proxmox-2 apply/reapply/rollback and fail-closed validation."""
import json
from pathlib import Path
import subprocess
import types

root = Path(__file__).resolve().parents[1]
source = root / "IaC/ansible/roles/icmp_timestamp_proxmox2/files/proxmox2-icmp-nft.py"
module = types.ModuleType("mock_proxmox2")
exec(compile(source.read_text(), str(source), "exec"), module.__dict__)

state = {"present": False, "drift": False, "fail_enum": False}
def result(code=0, stdout="", stderr=""):
    return subprocess.CompletedProcess([], code, stdout, stderr)

def mock_command(*args):
    if args[:2] == ("systemctl", "is-active"):
        return result(stdout="inactive\n")
    if args[:4] == ("/usr/sbin/ip", "-4", "-o", "addr"):
        return result(stdout="2: vmbr0 inet 192.168.2.71/24 scope global vmbr0\n")
    if args == ("/usr/sbin/nft", "list", "tables"):
        if state["fail_enum"]:
            return result(code=1, stderr="permission denied")
        return result(stdout="table inet homelab_icmp_proxmox2\n" if state["present"] else "")
    if args[:5] == ("/usr/sbin/nft", "-a", "list", "table", "inet"):
        if not state["present"]:
            return result(code=1)
        return result(stdout='table inet homelab_icmp_proxmox2 {\n chain input {\n type filter hook input priority filter; policy accept;\n ip protocol icmp icmp type timestamp-request counter packets 1 bytes 40 drop comment "homelab-icmp-proxmox2" # handle 7\n }\n}\n')
    if args[:5] == ("/usr/sbin/nft", "-j", "list", "table", "inet"):
        if not state["present"]:
            return result(code=1)
        objects = [
            {"metainfo": {"json_schema_version": 1}},
            {"table": {"family": "inet", "name": module.TABLE, "handle": 1}},
            {"chain": {"family": "inet", "table": module.TABLE, "name": "input", "handle": 1, "type": "filter", "hook": "input", "prio": 0, "policy": "accept"}},
            {"rule": {"family": "inet", "table": module.TABLE, "chain": "input", "handle": 7, "expr": []}},
        ]
        if state["drift"]:
            objects.append({"rule": {"family": "inet", "table": module.TABLE, "chain": "input", "handle": 8, "expr": []}})
        return result(stdout=json.dumps({"nftables": objects}))
    if args == ("/usr/sbin/nft", "delete", "table", "inet", module.TABLE):
        if state["drift"]:
            raise AssertionError("Drifted table must not be deleted")
        state["present"] = False
        return result()
    raise AssertionError("Unexpected command: " + repr(args))

def mock_run(argv, *, input=None, text=None, capture_output=None):
    assert argv == ["/usr/sbin/nft", "-c", "-f", "-"] or argv == ["/usr/sbin/nft", "-f", "-"]
    assert "policy accept" in input and "timestamp-request" in input and "flush" not in input
    if "-c" not in argv:
        state["present"] = True
    return result()

module.require_identity = lambda: None
module.command = mock_command
module.subprocess = types.SimpleNamespace(run=mock_run)
module.run_apply()
assert state["present"]
module.run_apply()
module.run_rollback()
assert not state["present"]
module.run_rollback()
state["present"] = True
state["drift"] = True
try:
    module.run_rollback()
    raise AssertionError("Drift rollback unexpectedly succeeded")
except RuntimeError:
    pass
state["present"] = False
state["drift"] = False
state["fail_enum"] = True
try:
    module.run_apply()
    raise AssertionError("Failed nft table enumeration unexpectedly accepted")
except RuntimeError:
    pass
print("ADMIN01 MOCK APPLY / IDEMPOTENCY / ROLLBACK / DRIFT GUARDS: PASS")
print("No live nftables, systemd or remote host commands invoked")
