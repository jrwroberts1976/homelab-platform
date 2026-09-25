"""Build a first-seen device notification with scan evidence."""

import json
from datetime import datetime, timezone
from email.message import EmailMessage

from device_queue import MAC_PATTERN


def build_device_message(mac, device, record, sender, recipient):
    """Prepare an email; never send one for a baseline device."""
    if not MAC_PATTERN.fullmatch(mac):
        raise ValueError("Invalid device MAC")
    if device.get("status") != "pending":
        raise ValueError("Device is not newly discovered")
    if record.get("status") not in ("complete", "partial", "failed"):
        raise ValueError("Device has no finished scan attempt")

    status = record["status"]
    profile = record.get("profile") if status != "failed" else None
    first_seen = datetime.fromtimestamp(
        device["discovered_at"], timezone.utc
    ).isoformat()

    lines = [
        "A previously unseen MAC address joined the homelab.",
        "",
        f"MAC: {mac}",
        f"Last DHCP IP: {device.get('last_ip', 'Unknown')}",
        f"Hostname: {str(device.get('hostname') or 'Unknown')[:100]}",
        f"First observed (UTC): {first_seen}",
        f"Profiling status: {status}",
    ]

    if status == "complete" or status == "partial":
        lines.append(f"Scanned IP: {record['profiled_ip']}")
        for protocol in ("tcp", "udp"):
            evidence = profile.get(protocol)
            lines.extend(["", f"{protocol.upper()} results:"])
            if evidence is None:
                lines.append("Unavailable")
                continue
            for os_match in evidence.get("os_matches", [])[:5]:
                lines.append(
                    f"Nmap OS estimate: {os_match.get('name')} "
                    f"(accuracy {os_match.get('accuracy')}%)"
                )
            for port in evidence.get("ports", []):
                service = port.get("service", {})
                lines.append(
                    f"{port.get('port')}/{protocol} "
                    f"{port.get('state')} "
                    f"{service.get('name', '')} "
                    f"{service.get('product', '')} "
                    f"{service.get('version', '')}"
                )

    if record.get("last_error"):
        lines.extend(["", f"Scan error: {record['last_error']}"])

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = f"Homelab: new device detected ({mac})"
    message.set_content("\n".join(lines) + "\n")
    message.add_attachment(
        json.dumps({
            "mac": mac, "device": device,
            "status": status, "profile": profile,
        }, indent=2).encode(),
        maintype="application",
        subtype="json",
        filename="device-profile.json",
    )
    return message
