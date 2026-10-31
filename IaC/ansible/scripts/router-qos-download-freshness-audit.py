#!/usr/bin/env python3
"""Offline-only session-bound observation audit; NEVER authorises recovery.

Holds the journal's flock while checking its pending state and the supplied
observation. No live kernel inspection, mutations, PPP hooks or state changes.
An eventual live implementation must gather evidence INSIDE the same lock.
"""
import importlib.util
from pathlib import Path
import sys

def load(filename, name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

journal_module = load("router-qos-download-durable-journal.py", "qos_freshness_journal")
adapter = load("router-qos-download-observation-adapter.py", "qos_freshness_adapter")

def inspect(journal_dir, expected_owned, expected_target, evidence, *,
            event_generation, observed_generation, observed_monotonic_ns,
            now_monotonic_ns, maximum_age_ns=2_000_000_000):
    result = {"status": "REFUSE_UNVERIFIED", "journal_recovery_authorized": False,
              "network_modified": False}
    if (not isinstance(event_generation, str) or not event_generation or
            observed_generation != event_generation or
            type(observed_monotonic_ns) is not int or
            type(now_monotonic_ns) is not int or
            type(maximum_age_ns) is not int or
            observed_monotonic_ns <= 0 or maximum_age_ns <= 0 or
            not 0 <= now_monotonic_ns - observed_monotonic_ns <= maximum_age_ns):
        return result
    try:
        j = journal_module.Journal(journal_dir)
        with j.locked():
            state = j.read()
            if (state["phase"] != "pending" or
                    state["owned"] != expected_owned or
                    state["target"] != expected_target):
                return result
            decision = adapter.interpret(evidence)
            if decision["status"] != "OBSERVED_CLEAN_NOT_AUTHORIZED":
                return result
            return {"status": "OBSERVED_FRESH_PENDING_NOT_AUTHORIZED",
                    "journal_recovery_authorized": False, "network_modified": False}
    except (journal_module.JournalError, OSError, TypeError, ValueError):
        return result
