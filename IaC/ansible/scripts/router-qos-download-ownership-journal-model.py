#!/usr/bin/env python3
"""Pure offline PPP ownership state machine: no host commands or file writes.

An interrupted operation enters RECOVERY_REQUIRED. Repeated/stale events must
not continue until externally verified recovery is explicitly acknowledged.
This models an intent journal; it is NOT a durable on-disk journal.
"""
from dataclasses import dataclass
import importlib.util
from pathlib import Path
import sys

path = Path(__file__).with_name("router-qos-download-ppp-event-replay.py")
spec = importlib.util.spec_from_file_location("qos_replay_journal", path)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

@dataclass
class Controller:
    owned: object = None
    pending: object = None
    recovery_required: bool = False

    def handle(self, event, *, failure_after_operation=None):
        if self.recovery_required or self.pending is not None:
            return "REFUSE_RECOVERY_REQUIRED", []
        proposed, decision, operations = mod.step(self.owned, event)
        if decision not in ("PLAN_INSTALL", "PLAN_TEARDOWN"):
            return decision, []
        # An operational implementation MUST persist this intent before any
        # mutation. Here only in-memory test state is updated.
        self.pending = (self.owned, proposed, decision)
        completed = []
        for operation in operations:
            completed.append(operation)
            if operation == failure_after_operation:
                self.recovery_required = True
                return "RECOVERY_REQUIRED", completed
        self.owned = proposed
        self.pending = None
        return decision, completed

    def recover(self, *, verified_clean, session=None):
        if not self.recovery_required or self.pending is None:
            return "REFUSE_NO_PENDING_RECOVERY"
        if not verified_clean:
            return "REFUSE_NOT_VERIFIED"
        # Recovery requires independent evidence the owned IFB and redirects
        # were removed. Neither stale nor future sessions are assumed live.
        self.owned = session
        self.pending = None
        self.recovery_required = False
        return "RECOVERY_ACKNOWLEDGED"
