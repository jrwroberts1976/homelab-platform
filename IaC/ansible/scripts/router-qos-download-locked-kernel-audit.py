#!/usr/bin/env python3
"""Read-only sensor inspection under an offline test journal lock.

The journal directory must already exist. This diagnostic never writes the
journal, authorises recovery, installs tc rules, or changes interfaces. A
journal flock does NOT lock the kernel or external PPP events.
"""
import importlib.util
from pathlib import Path
import sys
import time

def load(filename, name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

journal = load("router-qos-download-durable-journal.py", "qos_locked_probe_journal")
adapter = load("router-qos-download-observation-adapter.py", "qos_locked_probe_adapter")
collector = load("router-qos-download-sensor-readonly-collector.py", "qos_locked_probe_collector")

def audit(directory, owned, target, generation, *, collect=None, clock=None):
    result = {"status": "REFUSE_UNVERIFIED", "journal_recovery_authorized": False,
              "network_modified": False}
    collect = collect if collect is not None else collector.collect
    clock = clock if clock is not None else time.monotonic_ns
    try:
        journal.validate_session(owned)
        journal.validate_session(target)
        session = target if target is not None else owned
        if session is None or session["generation"] != generation:
            return result
        j = journal.Journal(directory)
        with j.locked():
            state = j.read()
            if (state["phase"] != "pending" or state["owned"] != owned or
                    state["target"] != target):
                return result
            before = clock()
            observation = collect()
            after = clock()
            if (type(before) is not int or type(after) is not int or
                    before <= 0 or after < before or after - before > 2_000_000_000):
                return result
            if adapter.interpret(observation)["status"] != "OBSERVED_CLEAN_NOT_AUTHORIZED":
                return result
            if j.read() != state:
                return result
            return {"status": "OBSERVED_UNDER_JOURNAL_LOCK_NOT_AUTHORIZED",
                    "journal_recovery_authorized": False, "network_modified": False}
    except (journal.JournalError, OSError, ValueError, TypeError, RuntimeError):
        return result

if __name__ == "__main__":
    raise SystemExit("Library only: no standalone mutation or recovery mode")
