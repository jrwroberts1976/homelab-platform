"""Extract IP-to-MAC observations from an Nmap discovery sweep."""

import ipaddress
import xml.etree.ElementTree as ET


def parse_sweep(xml):
    root = ET.fromstring(xml)
    if root.tag != "nmaprun":
        raise ValueError("Unexpected Nmap output")

    observed = {}

    for host in root.findall("host"):
        status = host.find("status")
        if status is None or status.get("state") != "up":
            continue

        addresses = {
            item.get("addrtype"): item.get("addr")
            for item in host.findall("address")
        }

        ip = addresses.get("ipv4")
        mac = addresses.get("mac")

        if ip and mac:
            ip = str(ipaddress.IPv4Address(ip))
            mac = mac.lower()

            if mac in observed and observed[mac] != ip:
                raise ValueError("Conflicting MAC observations")

            observed[mac] = ip

    if not observed:
        raise ValueError("No MAC addresses discovered")

    return observed
