#!/usr/bin/env python3
"""Render and smoke-test the Greenbone scan runner locally, without scanning.

Run from repository root. No credentials from the live host, Ansible inventory
access, Docker operations, or Greenbone network requests are made. A temporary
Unix socket simulates a GMP authenticate + get_tasks round trip.
"""
import ast
import tempfile
import threading
import xml.etree.ElementTree as ET
from pathlib import Path
import socket

from jinja2 import Environment, StrictUndefined

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "IaC/ansible/roles/greenbone_scanning/templates/homelab-greenbone-scan.py.j2"
TASK_NAME = "Homelab - Managed Infrastructure - Authenticated Daily"
TASK_ID = "d56f1370-1b6e-45c4-947e-e4ed1d0210a8"


def validate():
    with tempfile.TemporaryDirectory(prefix="greenbone-render-") as tempdir:
        directory = Path(tempdir)
        sock_path = directory / "gvmd.sock"
        credentials_path = directory / "runtime.env"
        credentials_path.write_text(
            "GREENBONE_ADMIN_USERNAME=dummy-user\n"
            "GREENBONE_ADMIN_PASSWORD=dummy-password\n"
        )

        context = {
            "greenbone_scanning_gvmd_socket": str(sock_path),
            "greenbone_scanning_runtime_env": str(credentials_path),
            "greenbone_scanning_managed_evidence_file": str(directory / "managed.json"),
            "greenbone_scanning_full_lan_evidence_file": str(directory / "full-lan.json"),
            "greenbone_scanning_smtp_host": "127.0.0.1",
            "greenbone_scanning_smtp_port": 25,
            "greenbone_scanning_mail_from": "test@example.invalid",
            "greenbone_scanning_mail_to": "test@example.invalid",
            "greenbone_scanning_poll_seconds": 60,
            "greenbone_scanning_scan_timeout_seconds": 21600,
            "greenbone_scanning_evidence_publisher": "/usr/bin/false",
            "greenbone_scanning_runner_managed_task_name": TASK_NAME,
            "greenbone_scanning_full_lan_task_name": "Homelab - Full LAN - Weekly",
            "greenbone_scanning_accepted_risks": [],
        }
        rendered = Environment(undefined=StrictUndefined).from_string(
            TEMPLATE.read_text()
        ).render(**context)
        ast.parse(rendered, filename=str(TEMPLATE))
        namespace = {"__name__": "greenbone_runner_validation"}
        exec(compile(rendered, str(TEMPLATE), "exec"), namespace)

        server = socket.socket(socket.AF_UNIX)
        server.bind(str(sock_path))
        server.listen(1)
        server.settimeout(3)
        faults = []

        def handle_client():
            try:
                with server.accept()[0] as connection:
                    connection.settimeout(3)
                    auth = ET.fromstring(connection.recv(4096))
                    assert auth.tag == "authenticate", "expected authentication first"
                    assert auth.findtext("credentials/username") == "dummy-user"
                    assert auth.findtext("credentials/password") == "dummy-password"
                    connection.sendall(b'<authenticate_response status="200"/>')
                    request = ET.fromstring(connection.recv(4096))
                    assert request.tag == "get_tasks", "expected get_tasks, not scan"
                    assert request.get("details") == "0"
                    reply = (
                        '<get_tasks_response status="200"><task id="'
                        + TASK_ID + '"><name>' + TASK_NAME
                        + '</name></task></get_tasks_response>'
                    )
                    split = len(reply) // 2
                    connection.sendall(reply[:split].encode())
                    connection.sendall(reply[split:].encode())
            except Exception as error:
                faults.append(error)
            finally:
                server.close()

        worker = threading.Thread(target=handle_client, daemon=True)
        worker.start()
        found = namespace["find_task_id"](TASK_NAME, timeout_seconds=3)
        worker.join(3)
        assert not worker.is_alive(), "mock GMP server did not finish"
        if faults:
            raise faults[0]
        assert found == TASK_ID, "task lookup returned unexpected ID"
        print("Greenbone runner Jinja render: PASS")
        print("Greenbone runner Python syntax: PASS")
        print("Mock Unix GMP auth and task lookup: PASS")
        print("No host, Docker, credential or vulnerability scan changes made.")


if __name__ == "__main__":
    validate()
