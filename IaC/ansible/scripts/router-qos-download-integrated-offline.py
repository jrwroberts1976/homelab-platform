#!/usr/bin/env python3
"""Offline integrated QoS transaction prototype. No CLI or real command runner.

A test-injected runner records commands; no kernel operations happen unless a
future, separately reviewed deployment adapter explicitly supplies one.
Journal lock spans intent, all commands, inspection and commit. Partial
failures remain pending and block subsequent operations.
"""
import importlib.util
from pathlib import Path
import sys

def load(name, alias):
    spec = importlib.util.spec_from_file_location(alias, Path(__file__).with_name(name))
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module

jmod = load("router-qos-download-durable-journal.py", "qos_integrated_journal")

class Refused(RuntimeError):
    pass

NAMESPACE = "qos-p5"
SOURCE = "qp5src"
IFB = "qp5ifb"
PREF = "49131"

def namespace_cmd(*command):
    return ["ip", "netns", "exec", NAMESPACE, *command]

def actions(install):
    if install:
        return [
            namespace_cmd("ip", "link", "add", IFB, "type", "ifb"),
            namespace_cmd("ip", "link", "set", IFB, "up"),
            namespace_cmd("tc", "qdisc", "add", "dev", IFB, "root", "cake", "bandwidth", "43mbit", "besteffort", "flows"),
            namespace_cmd("tc", "qdisc", "add", "dev", SOURCE, "clsact"),
            namespace_cmd("tc", "filter", "add", "dev", SOURCE, "ingress", "pref", PREF, "matchall", "action", "mirred", "egress", "redirect", "dev", IFB),
        ]
    return [
        namespace_cmd("tc", "filter", "del", "dev", SOURCE, "ingress", "pref", PREF),
        namespace_cmd("tc", "qdisc", "del", "dev", SOURCE, "clsact"),
        namespace_cmd("ip", "link", "del", "dev", IFB),
    ]

class OfflineLifecycle:
    def __init__(self, directory, *, runner, observe, watchdog):
        if not callable(runner) or not callable(observe) or not callable(watchdog):
            raise Refused("explicit injectable test collaborators required")
        self.journal = jmod.Journal(directory)
        self.runner = runner
        self.observe = observe
        self.watchdog = watchdog

    def transition(self, owned, target):
        jmod.validate_session(owned)
        jmod.validate_session(target)
        if owned == target:
            raise Refused("no-op transition")
        with self.journal.locked():
            state = self.journal.read()
            if state["phase"] != "clean" or state["owned"] != owned:
                raise Refused("stale or pending journal")
            # Watchdog and before-state are checked before a durable intent.
            if self.watchdog() is not True or self.observe(owned) is not True:
                raise Refused("watchdog/precondition not verified")
            j = {"version": 1, "phase": "pending", "owned": owned, "target": target}
            self.journal.write(j)
            try:
                for command in actions(target is not None):
                    if self.runner(command) is not True:
                        raise Refused("operation failed")
                if self.observe(target) is not True:
                    raise Refused("postcondition unverified")
                # No arbitrary externally_verified flag: postcondition checked
                # under the SAME lock, then directly commit the journal.
                self.journal.write({"version": 1, "phase": "clean", "owned": target, "target": None})
                return "COMMITTED"
            except Exception:
                # Leave pending; separate verified reconciliation is needed.
                raise

    def inspect(self):
        with self.journal.locked():
            return self.journal.read()
