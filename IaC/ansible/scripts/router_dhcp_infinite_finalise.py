#!/usr/bin/env python3
"""Offline DHCP finalisation decision logic. No production actions."""

from router_dhcp_infinite_recovery import sha256

ORIGINAL_SHA = "341d0c4271500127654c94b0bb4e21950f1929dce229bc7b9943bcd500042730"
CANDIDATE_SHA = "152e161010d5492173a39bd01140e359471f6a61a06886d079f5e0dfde6e2160"


def finalisation_decision(active_bytes, service_healthy, rollback_started):
    if rollback_started:
        return "REFUSE_ROLLBACK_STARTED"
    if sha256(active_bytes) != CANDIDATE_SHA:
        return "REFUSE_CONFIGURATION_MISMATCH"
    if service_healthy is not True:
        return "REFUSE_UNHEALTHY_SERVICE"
    return "FINALISATION_ALLOWED"
