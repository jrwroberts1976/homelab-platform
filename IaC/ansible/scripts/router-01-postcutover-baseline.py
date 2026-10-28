#!/usr/bin/env python3
"""Read-only Pi router performance snapshot, executed via Ansible stdin.

No files or configuration are written, no services are reloaded, and no
credentials, DHCP lease identities, or public WAN addresses are reported.
Uses one 3-second idle/CPU/interface sample and five low-rate WAN ICMP probes.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import time
from datetime import datetime, timezone


def text_file(path: str):
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except (FileNotFoundError, PermissionError, OSError):
        return None


def command(args: list[str], timeout: int = 8):
    try:
        result = subprocess.run(args, text=True, capture_output=True,
                                timeout=timeout, check=False)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return -1, "", str(exc)[:160]


def cpu_ticks():
    line = text_file("/proc/stat")
    if not line:
        return None
    numbers = [int(n) for n in line.splitlines()[0].split()[1:]]
    if len(numbers) < 5:
        return None
    return sum(numbers), numbers[3] + numbers[4]


def interfaces():
    result = {}
    for name in ("eth0", "eth1", "ppp0"):
        root = Path("/sys/class/net") / name
        if not root.exists():
            continue
        metrics = {}
        for key in ("rx_bytes", "tx_bytes", "rx_packets", "tx_packets",
                    "rx_errors", "tx_errors", "rx_dropped", "tx_dropped"):
            val = text_file(str(root / "statistics" / key))
            metrics[key] = int(val) if val and val.isdigit() else None
        for key in ("operstate", "carrier", "speed"):
            metrics[key] = text_file(str(root / key))
        result[name] = metrics
    return result


def memory():
    values = {}
    raw = text_file("/proc/meminfo") or ""
    for line in raw.splitlines():
        m = re.match(r"^(MemTotal|MemAvailable|SwapTotal|SwapFree):\s+(\d+)", line)
        if m:
            values[m.group(1)] = int(m.group(2))
    total = values.get("MemTotal", 0)
    available = values.get("MemAvailable", 0)
    return {
        "total_mib": round(total / 1024, 1),
        "available_mib": round(available / 1024, 1),
        "used_pct": round(100 * (total - available) / total, 1) if total else None,
        "swap_used_mib": round((values.get("SwapTotal", 0) - values.get("SwapFree", 0)) / 1024, 1),
    }


def root_disk():
    s = os.statvfs("/")
    total = s.f_blocks * s.f_frsize
    free = s.f_bavail * s.f_frsize
    return {
        "size_gib": round(total / (1024 ** 3), 1),
        "available_gib": round(free / (1024 ** 3), 1),
        "used_pct": round(100 * (total - free) / total, 1) if total else None,
    }


def pi_health():
    temp = text_file("/sys/class/thermal/thermal_zone0/temp")
    freq = text_file("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")
    governor = text_file("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
    throttled = None
    if shutil.which("vcgencmd"):
        rc, out, _ = command(["vcgencmd", "get_throttled"])
        throttled = out if rc == 0 else None
    return {
        "temperature_c": round(int(temp) / 1000, 1) if temp and temp.isdigit() else None,
        "cpu_frequency_mhz": round(int(freq) / 1000, 0) if freq and freq.isdigit() else None,
        "cpu_governor": governor,
        "pi_throttling_flags": throttled,
    }


def ping_test():
    if not shutil.which("ping"):
        return {"status": "ping utility not installed"}
    rc, out, err = command(
        ["ping", "-n", "-I", "ppp0", "-c", "5", "-i", "0.5", "-W", "2", "1.1.1.1"],
        timeout=15,
    )
    match_loss = re.search(r"(\d+(?:\.\d+)?)% packet loss", out)
    match_rtt = re.search(r"(?:rtt|round-trip) min/avg/max/(?:mdev|stddev) = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)", out)
    return {
        "target": "1.1.1.1 via ppp0",
        "packet_loss_pct": float(match_loss.group(1)) if match_loss else None,
        "latency_min_ms": float(match_rtt.group(1)) if match_rtt else None,
        "latency_avg_ms": float(match_rtt.group(2)) if match_rtt else None,
        "latency_max_ms": float(match_rtt.group(3)) if match_rtt else None,
        "ping_command_rc": rc,
        "diagnostic": err[:100] if rc != 0 else None,
    }


def lease_count():
    # Deliberately read only a COUNT, never reveal MAC/IP/name/client identity.
    for path in ("/var/lib/misc/dnsmasq.leases", "/var/lib/dnsmasq/dnsmasq.leases"):
        p = Path(path)
        if p.exists():
            try:
                return {"file_found": True, "current_rows": len(p.read_text().splitlines())}
            except OSError:
                return {"file_found": True, "current_rows": None}
    return {"file_found": False, "current_rows": None}


def socket_summary():
    rc, out, _ = command(["ss", "-lntuH"])
    if rc:
        return {"status": "ss failed"}
    hits = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        local = parts[4]
        if any(re.search(r":" + str(port) + r"$", local) for port in (22, 53, 67, 9100)):
            hits.append({"protocol": parts[0], "local_listener": local})
    return hits


def main():
    start = datetime.now(timezone.utc).isoformat(timespec="seconds")
    tick1, net1 = cpu_ticks(), interfaces()
    tick_time1 = time.monotonic()
    time.sleep(3)
    tick2, net2 = cpu_ticks(), interfaces()
    sample_seconds = time.monotonic() - tick_time1
    cpu_pct = None
    if tick1 and tick2 and tick2[0] > tick1[0]:
        cpu_pct = round(100 * (1 - (tick2[1] - tick1[1]) / (tick2[0] - tick1[0])), 1)
    interface_sample = {}
    for name, after in net2.items():
        before = net1.get(name, {})
        per_second = {}
        for key in ("rx_bytes", "tx_bytes"):
            newer, older = after.get(key), before.get(key)
            per_second[key.replace("_bytes", "_kbps")] = (
                round(max(0, newer - older) * 8 / 1000 / sample_seconds, 1)
                if newer is not None and older is not None else None
            )
        interface_sample[name] = {"counters": after, "sampled_rates": per_second}
    rc, default, _ = command(["ip", "-4", "route", "show", "default"])
    rc_lan, lan, _ = command(["ip", "-4", "-o", "addr", "show", "dev", "eth0"])
    rc_ppp, ppp, _ = command(["ip", "-4", "-o", "addr", "show", "dev", "ppp0"])
    # Do not print public WAN address. Show only whether PPP interface has IPv4.
    total_uptime = (text_file("/proc/uptime") or "0").split()[0]
    services = {}
    for unit in ("nftables", "router-pppoe", "dnsmasq", "unbound", "ssh", "prometheus-node-exporter"):
        _, status, _ = command(["systemctl", "is-active", unit])
        services[unit] = status
    load = text_file("/proc/loadavg") or ""
    output = {
        "timestamp_utc": start,
        "router_hostname": socket.gethostname(),
        "kernel": os.uname().release,
        "uptime_hours": round(float(total_uptime) / 3600, 2),
        "cpu_cores": os.cpu_count(),
        "load_1_5_15": load.split()[:3],
        "sample_seconds": round(sample_seconds, 1),
        "cpu_busy_pct_sample": cpu_pct,
        "pi_health": pi_health(),
        "memory": memory(),
        "root_disk": root_disk(),
        "network": {
            "eth0_has_192_168_2_1_24": (rc_lan == 0 and "inet 192.168.2.1/24" in lan),
            "default_route_uses_ppp0": rc == 0 and any("ppp0" in x for x in default.splitlines()),
            "ppp0_has_ipv4": rc_ppp == 0 and "inet " in ppp,
            "interfaces": interface_sample,
        },
        "services": services,
        "dhcp_lease_file": lease_count(),
        "listen_ports": socket_summary(),
        "wan_ping": ping_test(),
        "notes": [
            "CPU/network rates are one short idle snapshot, not a throughput benchmark",
            "Interface byte/error counters are cumulative since interface reset",
            "No WAN public address or DHCP client identities are collected",
            "Five ICMP WAN probes create minimal diagnostic traffic; no network config changes",
        ],
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
