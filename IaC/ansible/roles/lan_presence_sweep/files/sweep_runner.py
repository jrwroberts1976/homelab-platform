"""Discover LAN presence without hard-coded IP addresses."""

import ipaddress
import subprocess
from pathlib import Path

from presence_state import MAC
from sweep_guard import validated_observations


def run_discovery(interface="eth0"):
    address_output = subprocess.check_output(
        ["ip", "-4", "-o", "addr", "show", "dev", interface],
        text=True,
    )
    addresses = address_output.splitlines()
    if len(addresses) != 1:
        raise ValueError("Expected exactly one interface IPv4 address")

    local = ipaddress.ip_interface(addresses[0].split()[3])
    network = local.network

    if not network.is_private or network.num_addresses > 256:
        raise ValueError("Unexpected discovery subnet")

    result = subprocess.run(
        [
            "nmap", "-sn", "-n", "-PR", "--send-eth",
            "-e", interface, "-oX", "-", str(network),
        ],
        capture_output=True,
        text=True,
        timeout=90,
        check=True,
    )

    observed = validated_observations(
        result.stdout, network.num_addresses
    )

    if any(
        ipaddress.ip_address(ip) not in network
        for ip in observed.values()
    ):
        raise ValueError("Discovery returned an address outside the LAN")

    local_mac = Path(
        f"/sys/class/net/{interface}/address"
    ).read_text().strip().lower()

    if not MAC.fullmatch(local_mac):
        raise ValueError("Invalid local interface MAC")

    if local_mac in observed and observed[local_mac] != str(local.ip):
        raise ValueError("Conflicting local MAC address")

    observed[local_mac] = str(local.ip)
    return observed
