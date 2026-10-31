#!/usr/bin/env python3
"""Pure adapter between sensor collector JSON and offline cleanup evaluator.

Does not inspect the host, mutate network state, or authorise journal recovery.
The caller must provide a trusted snapshot; absent resources are INCONCLUSIVE.
"""
import importlib.util
from pathlib import Path
import sys

def load(filename, name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

ev = load("router-qos-download-cleanup-evidence.py", "qos_cleanup_evaluator_adapter")

def interpret(collected):
    if not isinstance(collected, dict):
        return {"status": "REFUSE_INVALID_SNAPSHOT", "journal_recovery_authorized": False}
    if collected.get("status") != "OBSERVED_NOT_AUTHORIZED":
        return {"status": "INCONCLUSIVE_OR_REFUSED", "journal_recovery_authorized": False}
    try:
        obs = collected["observations"]
        source, ifb, ingress, qdisc = (obs[k] for k in ("source", "ifb", "filter", "qdisc"))
        if any(not isinstance(o, dict) or
               set(o) != {"rc", "stdout", "stderr"} or
               type(o["rc"]) is not int or
               not isinstance(o["stdout"], str) or
               not isinstance(o["stderr"], str)
               for o in (source, ifb, ingress, qdisc)):
            raise ValueError("invalid command output")
        if ifb["stdout"].strip():
            raise ValueError("unexpected IFB stdout")
        snapshot = ev.Snapshot(
            namespace="qos-proof31",
            namespace_inode=collected["namespace_inode"],
            recorded_inode=collected["recorded_inode"],
            host_inode=collected["host_inode"],
            source_present=source["rc"] == 0 and bool(source["stdout"].strip()),
            ifb_lookup_rc=ifb["rc"],
            ifb_lookup_output=ifb["stderr"],
            ingress_rc=ingress["rc"],
            ingress_output=ingress["stdout"],
            qdisc_rc=qdisc["rc"],
            qdisc_output=qdisc["stdout"])
        ev.evaluate_clean(snapshot)
    except (KeyError, TypeError, ValueError, ev.Unverified):
        return {"status": "REFUSE_UNVERIFIED", "journal_recovery_authorized": False}
    return {"status": "OBSERVED_CLEAN_NOT_AUTHORIZED", "journal_recovery_authorized": False}
