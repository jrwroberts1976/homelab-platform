"""Render MAC-keyed discovery and scan status as Prometheus metrics."""

import ipaddress
import json
import re

from mac_vendors import lookup_vendor

MAC = re.compile(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\Z")
SCAN_STATUSES = {"reserved", "complete", "partial", "failed"}


def label(value):
    """Escape untrusted DHCP values for Prometheus labels."""
    value = str(value)[:128]
    return json.dumps(value, ensure_ascii=False).replace(
        "\r", r"\r"
    )


def render_metrics(collector, worker, vendors=None):
    if collector.get("schema_version") != 1:
        raise ValueError("Unsupported collector state")
    if worker.get("schema_version") != 1:
        raise ValueError("Unsupported worker state")

    devices = collector["devices"]
    profiles = worker["profiles"]

    lines = [
        "# HELP homelab_router_device_info MAC-keyed DHCP device identity.",
        "# TYPE homelab_router_device_info gauge",
        "# HELP homelab_router_device_adapter_vendor_info Network adapter OUI vendor, not necessarily the device manufacturer.",
        "# TYPE homelab_router_device_adapter_vendor_info gauge",
        "# HELP homelab_router_device_last_dhcp_seen_seconds Last DHCP observation.",
        "# TYPE homelab_router_device_last_dhcp_seen_seconds gauge",
        "# HELP homelab_router_device_scan_state Actual profiling status.",
        "# TYPE homelab_router_device_scan_state gauge",
        "# HELP homelab_router_device_port_info Nmap port findings; open|filtered is inconclusive.",
        "# TYPE homelab_router_device_port_info gauge",
        "# HELP homelab_router_device_os_estimate_accuracy_percent Nmap OS-match accuracy estimate, not verified identity.",
        "# TYPE homelab_router_device_os_estimate_accuracy_percent gauge",
        "# HELP homelab_router_device_os_match_accuracy_percent Ranked Nmap OS matches; accuracy is not a probability.",
        "# TYPE homelab_router_device_os_match_accuracy_percent gauge",
    ]

    for mac, device in sorted(devices.items()):
        if not MAC.fullmatch(mac):
            raise ValueError("Invalid inventory MAC")

        status = device.get("status")
        if status not in ("baseline", "pending"):
            raise ValueError("Invalid discovery status")

        ip = device.get("last_ip", "")
        if ip:
            ipaddress.IPv4Address(ip)

        identity = (
            f'mac={label(mac)},'
            f'ip={label(ip)},'
            f'hostname={label(device.get("hostname") or "")},'
            f'discovery_status={label(status)}'
        )
        lines.append(f"homelab_router_device_info{{{identity}}} 1")

        vendor = lookup_vendor(mac, vendors or {})
        if vendor:
            lines.append(
                "homelab_router_device_adapter_vendor_info"
                f'{{mac={label(mac)},vendor={label(vendor)}}} 1'
            )

        seen = device.get("last_inventory_seen")
        if isinstance(seen, (int, float)) and not isinstance(seen, bool):
            lines.append(
                f"homelab_router_device_last_dhcp_seen_seconds"
                f'{{mac={label(mac)}}} {seen}'
            )

        record = profiles.get(mac)
        if record:
            scan_status = record.get("status")
            if scan_status not in SCAN_STATUSES:
                raise ValueError("Invalid profiling status")
            lines.append(
                f"homelab_router_device_scan_state"
                f'{{mac={label(mac)},status={label(scan_status)}}} 1'
            )

        if record and record.get("status") in ("complete", "partial"):
            lines.extend(render_scan_evidence(mac, record))

    return "\n".join(lines) + "\n"


def render_scan_evidence(mac, record):
    """Publish only evidence from completed or partial Nmap scans."""
    profile = record.get("profile")
    if not isinstance(profile, dict):
        raise ValueError("Finished scan is missing its profile")

    metrics = []
    estimates = []
    for protocol in ("tcp", "udp"):
        evidence = profile.get(protocol)
        if evidence is None:
            continue
        if not isinstance(evidence, dict):
            raise ValueError("Invalid scan evidence")

        matches = evidence.get("os_matches", [])
        if not isinstance(matches, list):
            raise ValueError("Invalid OS-match evidence")

        estimates.extend(matches)
        for rank, match in enumerate(matches, start=1):
            if not isinstance(match, dict):
                raise ValueError("Invalid OS-match entry")

            name = match.get("name") or ""
            try:
                accuracy = int(match.get("accuracy"))
            except (ValueError, TypeError):
                continue

            if name and 0 <= accuracy <= 100:
                metrics.append(
                    "homelab_router_device_os_match_accuracy_percent"
                    f'{{mac={label(mac)},protocol={label(protocol)},'
                    f'rank={label(rank)},os={label(name)}}} {accuracy}'
                )

        for entry in evidence.get("ports", []):
            state = entry.get("state")
            if state not in ("open", "open|filtered"):
                continue
            number = entry.get("port")
            if type(number) is not int or not 1 <= number <= 65535:
                raise ValueError("Invalid port number")

            service = entry.get("service") or {}
            labels = (
                f"mac={label(mac)},protocol={label(protocol)},"
                f"port={label(number)},state={label(state)},"
                f"service={label(service.get('name') or '')},"
                f"product={label(service.get('product') or '')}"
            )
            metrics.append(
                f"homelab_router_device_port_info{{{labels}}} 1"
            )

    if estimates:
        best = estimates[0]
        name = best.get("name") or ""
        if name:
            try:
                accuracy = int(best.get("accuracy"))
            except (ValueError, TypeError):
                accuracy = -1
            if 0 <= accuracy <= 100:
                metrics.append(
                    "homelab_router_device_os_estimate_accuracy_percent"
                    f"{{mac={label(mac)},os={label(name)}}} {accuracy}"
                )

    return metrics
