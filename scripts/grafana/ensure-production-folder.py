#!/usr/bin/env python3
"""Idempotently create Homelab / Production Dashboards in Grafana 13.

Run on monitor-01 as root (reads /opt/monitoring/.env). Does not log secrets.
Run before deploying the new dashboard providers.
"""
import base64
import json
from pathlib import Path
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:3000"
PARENT_UID = "dfy4vfvi07rpca"
CHILD_UID = "homelab-production"
CHILD_TITLE = "Production Dashboards"
ENV_FILE = Path("/opt/monitoring/.env")


def read_password():
    for line in ENV_FILE.read_text().splitlines():
        if line.startswith("GF_SECURITY_ADMIN_PASSWORD="):
            value = line.split("=", 1)[1].strip()
            if value:
                return value.strip('"').strip("'")
    raise RuntimeError("Grafana admin password missing from protected environment")


def request(path, password, method="GET", payload=None):
    token = base64.b64encode(("admin:" + password).encode()).decode()
    headers = {"Authorization": "Basic " + token, "Accept": "application/json"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode()
    req = Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=15) as response:
            return response.status, json.load(response)
    except HTTPError as exc:
        if exc.code == 404:
            return 404, None
        raise RuntimeError("Grafana API returned HTTP " + str(exc.code)) from None


def main():
    if not ENV_FILE.is_file():
        raise RuntimeError("Run on monitor-01 with access to " + str(ENV_FILE))
    password = read_password()
    api = "/apis/folder.grafana.app/v1/namespaces/default/folders"
    status, parent = request(api + "/" + PARENT_UID, password)
    if status != 200 or parent["spec"]["title"] != "Homelab":
        raise RuntimeError("Expected Homelab parent folder UID/title do not match")

    status, child = request(api + "/" + CHILD_UID, password)
    if status == 404:
        payload = {
            "metadata": {
                "name": CHILD_UID,
                "annotations": {"grafana.app/folder": PARENT_UID},
            },
            "spec": {"title": CHILD_TITLE},
        }
        status, child = request(api, password, method="POST", payload=payload)
        if status not in (200, 201):
            raise RuntimeError("Unexpected folder creation status: " + str(status))
        print("Created Production Dashboards folder")
    elif status == 200:
        print("Production Dashboards folder already exists")
    else:
        raise RuntimeError("Unexpected folder lookup status: " + str(status))

    status, child = request(api + "/" + CHILD_UID, password)
    if (status != 200 or child["spec"]["title"] != CHILD_TITLE
            or child["metadata"].get("annotations", {}).get("grafana.app/folder") != PARENT_UID):
        raise RuntimeError("Folder verification failed: wrong name or parent")
    print("Verified: Homelab / Production Dashboards (" + CHILD_UID + ")")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        sys.exit(1)
