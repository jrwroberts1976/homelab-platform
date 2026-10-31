#!/usr/bin/env python3
"""TEST ONLY: strict PPP-event gate for disposable sensor watchdog proof.

Print exactly PLAN_INSTALL on the explicitly expected initial mock PPP event.
No network mutations. The shell harness remains responsible for verifying the
real independent watchdog and keeping all tc/ip work within its owned namespace.
"""
import importlib.util
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location("qos_replay_gate", Path(__file__).with_name("router-qos-download-ppp-event-replay.py"))
replay = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = replay
spec.loader.exec_module(replay)

def gate(event):
    if event != {"event": "up", "generation": "sensor-proof-A", "ifindex": 101}:
        raise ValueError("unexpected mock PPP event")
    proposed, decision, operations = replay.step(None, event)
    if (decision != "PLAN_INSTALL" or
            operations != ["arm_rollback", "verify_ppp_identity", "attach_owned_ifb"] or
            proposed.generation != "sensor-proof-A"):
        raise RuntimeError("PPP transition contract mismatch")
    return decision

if __name__ == "__main__":
    if sys.argv[1:] != ["--sensor-fixture"]:
        raise SystemExit("test fixture only")
    print(gate({"event": "up", "generation": "sensor-proof-A", "ifindex": 101}))
