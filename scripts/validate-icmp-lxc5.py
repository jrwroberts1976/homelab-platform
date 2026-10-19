#!/usr/bin/env python3
"""Offline tests for five LXC remediations. Never execute nft or use /etc."""
from pathlib import Path
import ast
import hashlib
import re
import tempfile
import types
import yaml

root = Path(__file__).resolve().parents[1]
helper_path = root / "IaC/ansible/roles/icmp_timestamp_lxc_batch/files/icmp_timestamp_lxc.py"
code = helper_path.read_text()
ast.parse(code)
compile(code, str(helper_path), "exec")
cut = root / "IaC/ansible/playbooks/greenbone-icmp-lxc5-cutover.yml"
undo = root / "IaC/ansible/playbooks/greenbone-icmp-lxc5-rollback.yml"
for item in (cut, undo):
    play = yaml.safe_load(item.read_text())
    assert len(play) == 1
    assert play[0]["serial"] == 1 and play[0]["any_errors_fatal"] is True
    assert play[0]["hosts"] == "mail-relay-01,dns-02,dns-01,zabbix-01,komodo-01"
assert "flush ruleset" not in code and '"reload"' not in code and '"restart"' not in code
assert "delegate_to: greenbone-01" in cut.read_text()
assert "'ICMP_TIMESTAMP_REPLIES_MATCHED=0'" in cut.read_text()
assert "rollback" in undo.read_text()

# Test against isolated per-host configurations, with mocked identity and nft access.
baseline = (
    "#!/usr/sbin/nft -f\n\nflush ruleset\n\n"
    "table inet filter {\n"
    "\tchain input {\n"
    "\t\ttype filter hook input priority filter;\n"
    "\t}\n"
    "\tchain forward {\n"
    "\t\ttype filter hook forward priority filter;\n"
    "\t}\n"
    "\tchain output {\n"
    "\t\ttype filter hook output priority filter;\n"
    "\t}\n"
    "}\n"
)
hosts = {"mail-relay-01": "192.168.2.54", "dns-02": "192.168.2.50",
         "dns-01": "192.168.2.51", "zabbix-01": "192.168.2.59",
         "komodo-01": "192.168.2.58"}
for hostname in hosts:
    with tempfile.TemporaryDirectory(prefix="icmp-lxc5-test-") as dirname:
        path = Path(dirname)
        # Do not execute helper's real host determination on admin-01.
        test_code = code.replace(
            'HOST = Path("/etc/hostname").read_text().strip()',
            "HOST = " + repr(hostname),
        )
        mod = types.ModuleType("isolated_" + hostname)
        exec(compile(test_code, str(helper_path), "exec"), mod.__dict__)
        assert mod.HOST == hostname and mod.EXPECTED[hostname] == hosts[hostname]
        mod.CONF = path / "nftables.conf"
        mod.BACKUP = path / "original.conf"
        mod.BASE_SHA = hashlib.sha256(baseline.encode()).hexdigest()
        mod.validate_identity = lambda: None
        mod.CONF.write_text(baseline)
        actual_mkstemp = tempfile.mkstemp
        def temp_inside(*args, **kwargs):
            if kwargs.get("dir") == "/etc":
                kwargs["dir"] = str(path)
            return actual_mkstemp(*args, **kwargs)
        mod.tempfile = types.SimpleNamespace(mkstemp=temp_inside)
        state = {"present": False}
        def mocked_command(*args):
            if args[:5] == ("/usr/sbin/nft", "-a", "list", "chain", "inet"):
                rule = (
                    f'\t\tip protocol icmp icmp type timestamp-request counter packets 0 bytes 0 '
                    f'drop comment "{mod.TAG}" # handle 9\n'
                ) if state["present"] else ""
                return ("table inet filter {\n\tchain input { # handle 1\n"
                        "\t\ttype filter hook input priority filter; policy accept;\n"
                        + rule + "\t}\n}\n")
            if args[:3] == ("/usr/sbin/nft", "-c", "-f"):
                assert mod.INSERT.rstrip("\n") in Path(args[3]).read_text()
                return ""
            if args[:3] == ("/usr/sbin/nft", "add", "rule"):
                assert not state["present"] and args[-1] == mod.TAG
                state["present"] = True
                return ""
            if args[:3] == ("/usr/sbin/nft", "delete", "rule"):
                assert state["present"] and args[-1] == "9"
                state["present"] = False
                return ""
            raise AssertionError("Unexpected command: " + repr(args))
        mod.run = mocked_command
        mod.main("apply")
        assert state["present"] and mod.INSERT in mod.CONF.read_text()
        mod.main("apply")
        mod.main("rollback")
        assert not state["present"] and mod.CONF.read_text() == baseline
        mod.main("rollback")
        assert not state["present"]
        print(hostname + " apply/idempotency/rollback PASS")
print("LXC5 OFFLINE VALIDATOR: PASS — no real firewall or host modifications")
