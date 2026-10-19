#!/usr/bin/env python3
"""Offline syntactic and safety checks, never invokes nft on live hosts."""
from pathlib import Path
import ast
import hashlib
import tempfile
import types
import yaml

root = Path(__file__).resolve().parents[1]
helper = root / "IaC/ansible/roles/icmp_timestamp_edge01/files/edge01_nft_timestamp.py"
cut = root / "IaC/ansible/playbooks/greenbone-icmp-timestamp-edge01-cutover.yml"
undo = root / "IaC/ansible/playbooks/greenbone-icmp-timestamp-edge01-rollback.yml"
text = helper.read_text()
ast.parse(text)
for path in (cut, undo):
    docs = yaml.safe_load(path.read_text())
    assert len(docs) == 1 and docs[0]['hosts'] == 'edge-01'
assert "flush ruleset" not in text
assert '"reload"' not in text and '"restart"' not in text
assert "homelab-icmp-edge01" in text
assert "nft" in text
assert "BACKUP.read_bytes()" in text
assert "EDGE01_ICMP_TIMESTAMP=NO_REPLY_OBSERVED" in cut.read_text()
assert "delegate_to: greenbone-01" in cut.read_text()
assert "rollback" in undo.read_text()
compile(text, str(helper), "exec")  # Syntax check in memory; avoid generating __pycache__

# Isolated helper integration exercise: no remote calls, mocked nft subprocess.
with tempfile.TemporaryDirectory(prefix="edge01-nft-mock-") as td:
    from pathlib import Path
    base = Path(td)
    baseline = (
        "#!/usr/sbin/nft -f\n\nflush ruleset\n\n"
        "table inet filter {\n"
        "        chain input {\n"
        "                type filter hook input priority filter;\n"
        "        }\n"
        "        chain forward {\n"
        "                type filter hook forward priority filter;\n"
        "        }\n"
        "        chain output {\n"
        "                type filter hook output priority filter;\n"
        "        }\n"
        "}\n"
    )
    mod = types.ModuleType("edge01_sandbox")
    exec(compile(text, str(helper), "exec"), mod.__dict__)
    mod.CONF = base / "nftables.conf"
    mod.BACKUP = base / "state" / "before"
    mod.BASE_SHA = hashlib.sha256(baseline.encode()).hexdigest()
    mod.validate_identity = lambda: None
    mod.CONF.write_text(baseline)
    state = {"rule": False, "handle": "17", "prefix": ""}
    def fake_run(*argv):
        if argv[:5] == ("/usr/sbin/nft", "-a", "list", "chain", "inet"):
            body = (f'                {state["prefix"]}icmp type timestamp-request '
                    f'counter packets 0 bytes 0 drop comment "{mod.TAG}" '
                    f'# handle {state["handle"]}\n') if state["rule"] else ""
            return ("table inet filter {\n"
                    "        chain input {\n"
                    "                type filter hook input priority filter; policy accept;\n"
                    + body + "        }\n}\n")
        if argv[:3] == ("/usr/sbin/nft", "-c", "-f"):
            assert mod.INSERT in Path(argv[3]).read_text()
            return ""
        if argv[:3] == ("/usr/sbin/nft", "add", "rule"):
            assert not state["rule"]
            state["rule"] = True
            return ""
        if argv[:3] == ("/usr/sbin/nft", "delete", "rule"):
            assert state["rule"] and argv[-1] == state["handle"]
            state["rule"] = False
            return ""
        raise AssertionError("Unexpected nft command: " + repr(argv))
    mod.run = fake_run
    for prefix in ("", "ip protocol icmp "):
        state.update(rule=False, prefix=prefix)
        mod.CONF.write_text(baseline)
        if mod.BACKUP.exists():
            mod.BACKUP.unlink()
        mod.main("inspect")
        mod.main("apply")
        assert mod.INSERT in mod.CONF.read_text() and state["rule"]
        mod.main("apply")
        assert state["rule"]
        mod.main("rollback")
        assert mod.CONF.read_text() == baseline and not state["rule"]
        mod.main("rollback")
    # An unrecognised live INPUT rule must halt before config modification.
    original_run = mod.run
    def unexpected_rule(*argv):
        out = original_run(*argv)
        if argv[:5] == ("/usr/sbin/nft", "-a", "list", "chain", "inet"):
            return out.replace("        }", "                tcp dport 22 accept # handle 15\n        }", 1)
        return out
    mod.run = unexpected_rule
    try:
        mod.main("apply")
        raise AssertionError("Unexpected INPUT rule was accepted")
    except RuntimeError as exc:
        assert "Unexpected INPUT rule" in str(exc)
print("EDGE01 mocked apply/idempotency/rollback, nft render variants and fail-closed guard: PASS")

print("EDGE01 offline syntax, scoped cutover, exact rollback and scanner assertions: PASS")
print("No live firewall, Proxmox, Docker or scan changes.")
