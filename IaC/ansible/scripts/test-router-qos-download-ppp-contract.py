#!/usr/bin/env python3
"""Offline, non-deploying PPP lifecycle contract checks. No network commands."""
from dataclasses import dataclass

@dataclass(frozen=True)
class State:
    generation: str | None = None
    ifindex: int | None = None
    owned: bool = False

def reconcile(state: State, event: str, generation: str, ifindex: int, foreign=False):
    if event == "up":
        if foreign:
            return state, "REFUSE_FOREIGN"
        if state.owned and state.generation == generation and state.ifindex == ifindex:
            return state, "NOOP"
        if state.owned:
            return state, "REQUIRE_VERIFIED_TEARDOWN"
        return State(generation, ifindex, True), "ARM_WATCHDOG_THEN_INSTALL"
    if event == "down":
        if not state.owned:
            return state, "NOOP"
        if (state.generation, state.ifindex) != (generation, ifindex):
            return state, "REFUSE_STALE_EVENT"
        return State(), "VERIFY_AND_REMOVE_OWNED"
    raise ValueError(event)

def run():
    empty = State()
    first, action = reconcile(empty, "up", "session-a", 5)
    assert action == "ARM_WATCHDOG_THEN_INSTALL"
    assert reconcile(first, "up", "session-a", 5) == (first, "NOOP")
    assert reconcile(first, "down", "session-a", 6) == (first, "REFUSE_STALE_EVENT")
    assert reconcile(first, "down", "session-b", 5) == (first, "REFUSE_STALE_EVENT")
    assert reconcile(first, "up", "session-b", 7) == (first, "REQUIRE_VERIFIED_TEARDOWN")
    assert reconcile(empty, "up", "session-b", 7, foreign=True) == (empty, "REFUSE_FOREIGN")
    assert reconcile(first, "down", "session-a", 5) == (empty, "VERIFY_AND_REMOVE_OWNED")
    print("OFFLINE_PPP_CONTRACT_PASS")

if __name__ == "__main__":
    run()
