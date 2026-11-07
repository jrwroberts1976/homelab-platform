#!/usr/bin/env python3
"""Offline-only OS evidence precedence projection for #297.

Not a deployed collector or exporter. Never converts a passive UA hint into
an authoritative OS, and never infers historical MAC ownership from an IP.
"""
from collections import Counter


def resolve(ip, mac, membership, nmap_record=None, passive_hints=()):
    """Return provenance-labelled assessment without performing I/O.

    membership is the existing Zabbix comparison category; caller must supply
    a matched identity result (never infer host membership from a UA).
    """
    categories = {
        "zabbix_os_authoritative", "zabbix_without_os",
        "ambiguous", "unmatched_inventory",
    }
    if membership not in categories:
        raise ValueError("Unrecognised Zabbix classification")
    result = {
        "ip": ip,
        "os_source": "unknown",
        "os_family": None,
        "confidence": "none",
        "attribution": "unverified",
        "status": "unknown",
    }
    if membership == "zabbix_os_authoritative":
        result.update(os_source="zabbix", confidence="authoritative",
                      status="os_known_in_zabbix", attribution="managed_host")
        # Zabbix OS family/name is deliberately not guessed from a membership
        # class. Its existing item remains source of truth.
        return result
    if membership in ("zabbix_without_os", "ambiguous"):
        result["status"] = ("managed_os_missing" if membership == "zabbix_without_os"
                            else "identity_ambiguous")
        return result

    if isinstance(nmap_record, dict):
        evidence = nmap_record.get("profile")
        tcp = evidence.get("tcp") if isinstance(evidence, dict) else None
        matches = tcp.get("os_matches") if isinstance(tcp, dict) else None
        if (
            nmap_record.get("profiled_ip") == ip
            and nmap_record.get("status") in ("complete", "partial")
            and not (evidence or {}).get("tcp_evidence_stale")
            and isinstance(matches, list) and matches
            and isinstance(matches[0], dict)
            and isinstance(matches[0].get("name"), str)
            and matches[0]["name"].strip()
        ):
            # No arbitrary OS family parsing from Nmap's model description.
            result.update(os_source="nmap", status="nmap_os_fingerprint",
                          confidence="candidate", attribution="scan_ip_only")
            return result

    # A passive candidate is an IP-scoped, self-reported family, not a host
    # identity or verified operating system. Conflicting families are retained
    # as unresolved instead of choosing the most frequent.
    families = Counter()
    for hint in passive_hints:
        if not isinstance(hint, dict) or hint.get("src_ip") != ip:
            continue
        family = hint.get("os_family_hint")
        count = hint.get("observations")
        if (family in {"Linux", "Windows", "macOS", "Android", "iOS/iPadOS", "ChromeOS"}
                and type(count) is int and count > 0):
            families[family] += count
    if len(families) > 1:
        result["status"] = "passive_conflicting_hints"
    elif families:
        result.update(os_source="http_user_agent", os_family=next(iter(families)),
                      confidence="low", attribution="historical_ip_unverified",
                      status="passive_candidate_only")
    elif isinstance(nmap_record, dict) and nmap_record.get("status") == "partial":
        result["status"] = "nmap_partial_no_os"
    return result
