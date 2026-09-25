"""Verify a device's identity from Nmap ARP discovery XML."""

import ipaddress
import xml.etree.ElementTree as ET


def verify_mac_ip(xml, expected_ip, expected_mac):
    """Fail closed unless exactly one live host matches both."""
    expected_ip = str(ipaddress.IPv4Address(expected_ip))
    expected_mac = expected_mac.lower()

    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return False

    if root.tag != "nmaprun":
        return False

    finished = root.find("./runstats/finished")
    if finished is None or finished.get("exit") != "success":
        return False

    matches = []
    for host in root.findall("host"):
        addresses = {
            a.get("addrtype"): a.get("addr", "").lower()
            for a in host.findall("address")
        }
        if addresses.get("ipv4") == expected_ip:
            status = host.find("status")
            matches.append(
                status is not None
                and status.get("state") == "up"
                and addresses.get("mac") == expected_mac
            )

    return len(matches) == 1 and matches[0]


def probe_mac_ip(ip, mac, runner, interface="eth0"):
    """Run ARP discovery and verify the expected device identity."""
    import re

    target = ipaddress.IPv4Address(ip)
    network = ipaddress.ip_network("192.168.2.0/24")

    if target not in network:
        raise ValueError("Target is outside the approved LAN")

    if not re.fullmatch(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}", mac.lower()):
        raise ValueError("Invalid target MAC")

    if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_.-]{0,15}", interface):
        raise ValueError("Invalid network interface")

    result = runner(
        ["nmap", "-sn", "-PR", "-n", "--send-eth",
         "-e", interface, "-oX", "-", str(target)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    return result.returncode == 0 and verify_mac_ip(
        result.stdout, str(target), mac
    )
