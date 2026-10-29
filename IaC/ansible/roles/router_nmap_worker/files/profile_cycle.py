"""Run one MAC-keyed profiling cycle under the global worker lock."""

import time

from worker import prepare_verified_scan
from scan_runner import scan_tcp, scan_udp
from target_guard import post_scan_identity_verified
from worker_state import (
    mark_scan_complete, mark_scan_failed, mark_scan_partial,
)


def run_profile_once(collector, profiles, lock, runner,
                     interface="eth0", now=None, cooldown=86400):
    started = time.time() if now is None else now

    with prepare_verified_scan(
        collector, profiles, lock, runner,
        interface=interface, now=started, cooldown=cooldown
    ) as device:
        if device is None:
            return None

        mac, ip = device["mac"], device["ip"]

        try:
            tcp = scan_tcp(ip, runner, interface)

            if not post_scan_identity_verified(
                collector, mac, ip, runner, interface
            ):
                raise RuntimeError("Identity changed after TCP scan")

            try:
                udp = scan_udp(ip, runner, interface)
            except Exception as exc:
                reason = f"{type(exc).__name__}: {exc}"
                mark_scan_partial(
                    profiles, collector, mac, ip, tcp,
                    time.time() if now is None else now,
                    runner, reason, interface
                )
                return {"mac": mac, "status": "partial"}

            mark_scan_complete(
                profiles, collector, mac, ip, tcp, udp,
                time.time() if now is None else now,
                runner, interface
            )
            return {"mac": mac, "status": "complete"}

        except Exception as exc:
            reason = f"{type(exc).__name__}: {exc}"
            mark_scan_failed(profiles, mac, ip, reason)
            return {"mac": mac, "status": "failed", "error": reason}
