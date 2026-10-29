#!/usr/bin/env python3
"""Validate dnsmasq DHCPACK journal entries for forwarding."""

import ipaddress
import re

DHCP_ACK = re.compile(
    r"^DHCPACK\(eth0\)\s+"
    r"(?P<ip>\S+)\s+"
    r"(?P<mac>(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})"
    r"(?:\s+(?P<hostname>[A-Za-z0-9._-]+))?$"
)


def format_event(entry):
    if entry.get("SYSLOG_IDENTIFIER") != "dnsmasq-dhcp":
        return None

    if entry.get("_SYSTEMD_UNIT") != "dnsmasq.service":
        return None

    message = entry.get("MESSAGE")
    if not isinstance(message, str):
        return None

    match = DHCP_ACK.fullmatch(message)
    if not match:
        return None

    try:
        ip = ipaddress.IPv4Address(match.group("ip"))
    except ipaddress.AddressValueError:
        return None

    if ip not in ipaddress.IPv4Network("192.168.2.0/24"):
        return None

    pid = str(entry.get("SYSLOG_PID") or entry.get("_PID") or "")
    if not pid.isdecimal() or not 1 <= int(pid) <= 4194304:
        return None

    return f"dnsmasq-dhcp[{pid}]: {message}"


def format_syslog_packet(entry, hostname="router-01"):
    """Build a traditional syslog packet for the existing receiver."""
    from datetime import datetime, timezone

    event = format_event(entry)
    if event is None:
        return None

    timestamp = datetime.now(timezone.utc).strftime("%b %d %H:%M:%S")
    return f"<134>{timestamp} {hostname} {event}".encode("utf-8")


def forward_entries(lines, send_packet, hostname="router-01"):
    """Forward valid JSON journal records using an injected sender."""
    import json

    forwarded = 0
    for line in lines:
        try:
            entry = json.loads(line)
        except (ValueError, TypeError):
            continue

        if not isinstance(entry, dict):
            continue

        packet = format_syslog_packet(entry, hostname)
        if packet is None:
            continue

        send_packet(packet)
        forwarded += 1

    return forwarded




def run(host, port):
    """Forward new DHCP journal events, cleaning up journalctl on exit."""
    import socket
    import subprocess

    command = [
        "/usr/bin/journalctl",
        "--unit=dnsmasq.service",
        "--follow",
        "--lines=0",
        "--output=json",
        "--no-pager",
    ]

    process = None
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            forward_entries(
                process.stdout,
                lambda packet: sock.sendto(packet, (host, port)),
            )
            raise RuntimeError(
                f"journalctl stream ended; status={process.poll()}"
            )
    finally:
        if process is not None:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            if process.stdout is not None:
                process.stdout.close()


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=5514)
    args = parser.parse_args()

    run(args.host, args.port)


if __name__ == "__main__":
    main()
