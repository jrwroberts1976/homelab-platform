#!/usr/bin/env python3
"""Test-only isolated IFB/CAKE executor. NO CLI, hook, or production deployment.

Only accepts the exact disposable namespace and interface names. The runner is
injected so that all operations can be tested without touching host networking.
A live runner must additionally verify namespace ownership and arm an
independent watchdog BEFORE this class is allowed to execute.
"""
from dataclasses import dataclass

NAMESPACE = "qos-p5"
SOURCE = "qp5src"
IFB = "qp5ifb"
PREF = "49131"

class Refused(RuntimeError):
    pass

@dataclass(frozen=True)
class NamespaceIdentity:
    name: str
    inode: int
    host_inode: int
    owned_inode: int

    def verify(self):
        if (self.name != NAMESPACE or self.inode <= 0 or
                self.inode == self.host_inode or self.inode != self.owned_inode):
            raise Refused("namespace ownership mismatch")

class IsolatedExecutor:
    def __init__(self, runner, identity, *, watchdog_armed=False, watchdog_evidence=None, watchdog_validator=None):
        self.runner = runner
        self.identity = identity
        self.watchdog_armed = watchdog_armed
        self.watchdog_evidence = watchdog_evidence
        self.watchdog_validator = watchdog_validator
        self.installed = False
        self.pending = False

    def _call(self, *args):
        self.identity.verify()
        return self.runner(["ip", "netns", "exec", NAMESPACE, *args])

    def install(self):
        self.identity.verify()
        if not self.watchdog_armed or self.watchdog_evidence is None or self.watchdog_validator is None:
            raise Refused("independent watchdog evidence not supplied")
        try:
            self.watchdog_validator(self.watchdog_evidence)
        except Exception as error:
            raise Refused("independent watchdog evidence invalid") from error
        if (self.watchdog_evidence.namespace != self.identity.name or
                self.watchdog_evidence.namespace_inode != self.identity.inode):
            raise Refused("watchdog bound to different namespace")
        if self.installed or self.pending:
            raise Refused("already installed or partial install")
        # Precondition results must be verified by the future live wrapper:
        # the namespace contains no qp5ifb, and qp5src has no ingress rules.
        self.pending = True
        try:
            self._call("ip", "link", "add", IFB, "type", "ifb")
            self._call("ip", "link", "set", IFB, "up")
            self._call("tc", "qdisc", "add", "dev", IFB, "root", "cake", "bandwidth", "43mbit", "besteffort", "flows")
            self._call("tc", "qdisc", "add", "dev", SOURCE, "clsact")
            self._call("tc", "filter", "add", "dev", SOURCE, "ingress", "pref", PREF, "matchall",
                       "action", "mirred", "egress", "redirect", "dev", IFB)
            self.installed = True
            self.pending = False
        except Exception:
            # Intent remains pending. DO NOT treat this as a successful rollback:
            # independent watchdog / verified recovery must reconcile partial state.
            raise

    def teardown(self):
        self.identity.verify()
        if not self.installed or self.pending:
            raise Refused("teardown requires fully verified owned installation")
        self._call("tc", "filter", "del", "dev", SOURCE, "ingress", "pref", PREF)
        self._call("tc", "qdisc", "del", "dev", SOURCE, "clsact")
        self._call("ip", "link", "del", "dev", IFB)
        self.installed = False
