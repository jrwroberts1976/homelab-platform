#!/usr/bin/env python3
"""Idempotently create only the existing full-LAN task using deployed GMP runner."""
import runpy
import xml.etree.ElementTree as ET

RUNNER = "/usr/local/sbin/homelab-greenbone-scan"
TASK_NAME = "Homelab - Full LAN - Weekly"
TARGET = "23d32a1e-ce0c-4d89-9bc5-76da688b2909"
CONFIG = "daba56c8-73ec-11df-a475-002264764cea"
SCANNER = "08b69003-5fc2-4037-a479-93b440211c73"

client = runpy.run_path(RUNNER, run_name="greenbone_task_maintenance")
gmp = client["gmp"]

targets = gmp('<get_targets filter="rows=-1"/>')
match = [t for t in targets.findall(".//target") if t.get("id") == TARGET]
if len(match) != 1 or match[0].findtext("name") != "Homelab - Full LAN" or match[0].findtext("hosts") != "192.168.2.0/24":
    raise RuntimeError("Expected full LAN target not found or changed")
tasks = gmp('<get_tasks details="1" filter="rows=-1"/>')
matches = [t for t in tasks.findall(".//task") if t.findtext("name") == TASK_NAME]
if len(matches) > 1:
    raise RuntimeError("Duplicate full LAN task names")
if matches:
    task = matches[0]
    for field, expected in (("target", TARGET), ("config", CONFIG), ("scanner", SCANNER)):
        obj = task.find(field)
        if obj is None or obj.get("id") != expected:
            raise RuntimeError("Existing task has unexpected " + field)
    print("FULL_LAN_TASK=ALREADY_PRESENT ID=" + task.get("id", ""))
else:
    xml = ET.Element("create_task")
    ET.SubElement(xml, "name").text = TASK_NAME
    ET.SubElement(xml, "comment").text = "Ansible-managed full-LAN weekly task; scheduled by systemd"
    for field, ref in (("config", CONFIG), ("target", TARGET), ("scanner", SCANNER)):
        ET.SubElement(xml, field, {"id": ref})
    result = gmp(ET.tostring(xml, encoding="unicode"))
    if not result.get("id"):
        raise RuntimeError("Greenbone did not return created task ID")
    print("FULL_LAN_TASK=CREATED ID=" + result.get("id"))
