#!/usr/bin/env python3
"""Short, read-only, direct Unix-socket GMP authentication/task lookup."""
import fcntl
import signal
import socket
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

RUNTIME_ENV = Path("/etc/greenbone-scanning/runtime.env")
SOCKET = "/var/lib/docker/volumes/greenbone-community-edition_gvmd_socket_vol/_data/gvmd.sock"
LOCK = "/run/lock/homelab-greenbone-scan.lock"
TASK = "Homelab - Managed Infrastructure - Authenticated Daily"

def deadline(_signal, _frame):
    raise TimeoutError("DIRECT_GMP_DEADLINE_EXCEEDED")

def request(sock, command):
    sock.sendall(ET.tostring(command, encoding="utf-8"))
    parser = ET.XMLPullParser(events=("start", "end"))
    depth = 0
    while True:
        payload = sock.recv(65536)
        if not payload:
            raise RuntimeError("SOCKET_CLOSED")
        parser.feed(payload)
        for event, node in parser.read_events():
            depth += 1 if event == "start" else -1
            if depth == 0:
                return node

def main():
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(30)
    values = {}
    for line in RUNTIME_ENV.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            if key in ("GREENBONE_ADMIN_USERNAME", "GREENBONE_ADMIN_PASSWORD"):
                values[key] = value
    if not values.get("GREENBONE_ADMIN_USERNAME") or not values.get("GREENBONE_ADMIN_PASSWORD"):
        raise RuntimeError("MISSING_CREDENTIALS")

    # Same flock as the existing runner; do not create or modify lock contents.
    with LOCK_PATH_OPEN() as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with socket.socket(socket.AF_UNIX) as sock:
            sock.settimeout(12)
            sock.connect(SOCKET)
            auth = ET.Element("authenticate")
            credentials = ET.SubElement(auth, "credentials")
            ET.SubElement(credentials, "username").text = values["GREENBONE_ADMIN_USERNAME"]
            ET.SubElement(credentials, "password").text = values["GREENBONE_ADMIN_PASSWORD"]
            print("DIRECT_GMP_STAGE=authenticate", flush=True)
            result = request(sock, auth)
            print("DIRECT_GMP_AUTH_STATUS=" + str(result.get("status")), flush=True)
            if result.get("status") != "200":
                raise RuntimeError("AUTH_REJECTED")
            print("DIRECT_GMP_STAGE=get_tasks", flush=True)
            result = request(sock, ET.Element("get_tasks", details="0"))
            print("DIRECT_GMP_TASKS_STATUS=" + str(result.get("status")), flush=True)
            if result.get("status") != "200":
                raise RuntimeError("TASK_QUERY_REJECTED")
            matches = [
                task for task in result.findall(".//task")
                if task.findtext("name", "").strip() == TASK
            ]
            print("DIRECT_GMP_MANAGED_TASK_MATCHES=" + str(len(matches)), flush=True)
            if len(matches) != 1:
                raise RuntimeError("MANAGED_TASK_NOT_UNIQUE")
            print("DIRECT_GMP_CHECK=PASS", flush=True)

def LOCK_PATH_OPEN():
    return open(LOCK, "r+")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Deliberately do not print exception text or raw server XML:
        # these could disclose data on auth failures.
        print("DIRECT_GMP_ERROR_TYPE=" + type(exc).__name__, flush=True)
        sys.exit(1)
