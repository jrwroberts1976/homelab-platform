#!/usr/bin/env python3
"""Phase 5 adapter: PPP event decisions -> isolated QoS operation calls.

DEFAULT DRY-RUN. This adapter never invokes ip/tc/systemd, and cannot be
installed as a PPP hook. Real namespace executor must be separately reviewed.
"""
import importlib.util
from pathlib import Path
import sys

path = Path(__file__).with_name("router-qos-download-ppp-event-replay.py")
spec = importlib.util.spec_from_file_location("qos_event_replay", path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class RecordingBackend:
    def __init__(self):
        self.calls = []

    def apply(self, operation):
        # Records decisions only. NEVER mutates the OS.
        self.calls.append(operation)


class Integration:
    def __init__(self, backend=None):
        self.backend = backend or RecordingBackend()
        self.owned = None

    def event(self, payload, *, fail_at=None):
        proposal, decision, operations = module.step(self.owned, payload)
        if decision not in ("PLAN_INSTALL", "PLAN_TEARDOWN"):
            return decision
        # All operations must be accepted before changing in-memory ownership.
        # No filesystem or kernel state is committed in this fixture.
        for operation in operations:
            if operation == fail_at:
                return "INJECTED_FAILURE_UNCOMMITTED"
            self.backend.apply(operation)
        self.owned = proposal
        return decision


def main():
    controller = Integration()
    sequence = [
        {"event": "up", "generation": "A", "ifindex": 5},
        {"event": "up", "generation": "A", "ifindex": 5},
        {"event": "down", "generation": "A", "ifindex": 5},
        {"event": "up", "generation": "B", "ifindex": 7},
    ]
    for event in sequence:
        print(controller.event(event))
    print("DRY_RUN_ONLY network_modified=false")


if __name__ == "__main__":
    main()
