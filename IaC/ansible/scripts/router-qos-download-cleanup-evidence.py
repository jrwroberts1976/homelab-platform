#!/usr/bin/env python3
"""OFFLINE-ONLY Phase 5 cleanup evidence evaluation.

Accepts captured command results from a trusted future read-only probe.
It never executes commands and cannot authorize a journal transition.
Strictly scoped to the disposable sensor namespace, not production ppp0.
"""
from dataclasses import dataclass

class Unverified(RuntimeError):
    pass

@dataclass(frozen=True)
class Snapshot:
    namespace: str
    namespace_inode: int
    recorded_inode: int
    host_inode: int
    source_present: bool
    ifb_lookup_rc: int
    ifb_lookup_output: str
    ingress_rc: int
    ingress_output: str
    qdisc_rc: int
    qdisc_output: str

def evaluate_clean(snapshot):
    if type(snapshot) is not Snapshot:
        raise Unverified("unexpected snapshot type")
    if (snapshot.namespace != "qos-proof31" or
            type(snapshot.namespace_inode) is not int or
            type(snapshot.recorded_inode) is not int or
            type(snapshot.host_inode) is not int or
            snapshot.namespace_inode <= 0 or
            snapshot.namespace_inode != snapshot.recorded_inode or
            snapshot.namespace_inode == snapshot.host_inode):
        raise Unverified("namespace ownership not proven")
    if snapshot.source_present is not True:
        raise Unverified("source interface missing")
    if snapshot.ifb_lookup_rc != 1:
        raise Unverified("IFB absence not established by expected lookup failure")
    if not isinstance(snapshot.ifb_lookup_output, str) or "does not exist" not in snapshot.ifb_lookup_output:
        raise Unverified("IFB lookup error ambiguous")
    if snapshot.ingress_rc != 0 or snapshot.qdisc_rc != 0:
        raise Unverified("tc inspection failed")
    if not isinstance(snapshot.ingress_output, str) or snapshot.ingress_output.strip():
        raise Unverified("ingress filters remain or output ambiguous")
    if not isinstance(snapshot.qdisc_output, str):
        raise Unverified("qdisc output ambiguous")
    # qdisc may have the source's ordinary noqueue; refuse any clsact/ingress.
    if any(word in snapshot.qdisc_output.lower() for word in ("clsact", "ingress")):
        raise Unverified("ingress qdisc remains")
    return {"observed_clean": True, "journal_recovery_authorized": False,
            "network_modified": False}
