"""Execute approved Nmap scans and extract OS/service evidence."""

import ipaddress
import re

from scan_evidence import parse_host

UDP_PORTS = "53,67,68,69,123,137,138,161,500,514,1900,4500,5353,5683"


def validate_target(ip, interface):
    target = ipaddress.IPv4Address(ip)
    if target not in ipaddress.ip_network("192.168.2.0/24"):
        raise ValueError("Scan target outside approved LAN")
    if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_.-]{0,15}", interface):
        raise ValueError("Invalid network interface")
    return str(target)


def execute_scan(command, ip, runner, timeout):
    result = runner(
        command, capture_output=True, text=True,
        timeout=timeout, check=False
    )
    if result.returncode != 0:
        raise RuntimeError("Nmap scan failed")
    return parse_host(result.stdout, ip)


def scan_tcp(ip, runner, interface="eth0"):
    ip = validate_target(ip, interface)
    command = [
        "nmap", "-sS", "-sV", "--version-all",
        "-O", "--osscan-guess", "--max-os-tries", "2",
        "-Pn", "-n", "-T3", "--max-retries", "2",
        "--host-timeout", "20m", "-p-",
        "-e", interface, "-oX", "-", ip,
    ]
    return execute_scan(command, ip, runner, 1250)


def scan_udp(ip, runner, interface="eth0"):
    ip = validate_target(ip, interface)
    command = [
        "nmap", "-sU", "-sV", "--version-light",
        "-Pn", "-n", "-T3", "--max-retries", "1",
        "--host-timeout", "10m", "--send-eth", "-p", UDP_PORTS,
        "-e", interface, "-oX", "-", ip,
    ]
    return execute_scan(command, ip, runner, 650)
