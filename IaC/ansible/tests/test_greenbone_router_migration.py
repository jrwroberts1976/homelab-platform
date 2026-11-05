"""Offline regression checks for the staged Greenbone router migration."""
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "roles/greenbone_scanning/templates/greenbone-router-migration.py.j2"


def migration_namespace():
    source = TEMPLATE.read_text()
    source = source.replace("{{ greenbone_scanning_authenticated_target_name }}", "Homelab - Managed Infrastructure - Authenticated")
    source = source.replace("{{ greenbone_scanning_authenticated_task_name }}", "Homelab - Managed Infrastructure - Authenticated Daily")
    source = source.replace("{{ 'True' if greenbone_router_migration_approved | default(false) | bool else 'False' }}", "True")
    ns = {"__name__": "greenbone_migration_under_test"}
    exec(compile(source, str(TEMPLATE), "exec"), ns)
    return ns


def existing():
    target = ET.Element("target", {"id": "1c8418b5-1cae-4cca-8535-4700c2d2835b"})
    ET.SubElement(target, "name").text = "Homelab - Managed Infrastructure - Authenticated"
    ET.SubElement(target, "hosts").text = "192.168.2.48, 192.168.2.220"
    ssh = ET.SubElement(target, "ssh_credential", {"id": "credential-id"})
    ET.SubElement(ssh, "port").text = "22"
    ET.SubElement(target, "port_list", {"id": "port-list-id"})
    ET.SubElement(target, "alive_tests").text = "Scan Config Default"
    ET.SubElement(target, "exclude_hosts").text = "192.168.2.254"
    task = ET.Element("task", {"id": "02b610fc-647a-4fb8-98c3-7763e0425c34"})
    ET.SubElement(task, "target", {"id": target.get("id")})
    ET.SubElement(task, "config", {"id": "daba56c8-73ec-11df-a475-002264764cea"})
    ET.SubElement(task, "scanner", {"id": "08b69003-5fc2-4037-a479-93b440211c73"})
    ET.SubElement(task, "status").text = "Done"
    return target, task


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.ns = migration_namespace()
        self.target, self.task = existing()
        self.desired = {"192.168.2.1", "192.168.2.48"}
        self.requests = []

    def gmp(self, xml):
        self.requests.append(ET.fromstring(xml))
        if self.requests[-1].tag == "create_target":
            return '<create_target_response status="201" id="new-target"/>'
        if self.requests[-1].tag == "create_task":
            return '<create_task_response status="201" id="new-task"/>'
        raise RuntimeError("Unexpected GMP write")

    def test_legacy_preflight_accepted(self):
        self.ns["verified_existing"](self.target, self.task, "credential-id", self.desired)

    def test_refuses_unexpected_legacy_host(self):
        self.target.find("hosts").text += ",192.168.2.99"
        with self.assertRaisesRegex(RuntimeError, "drifted"):
            self.ns["verified_existing"](self.target, self.task, "credential-id", self.desired)

    def test_refuses_running_legacy_task(self):
        self.task.find("status").text = "Running"
        with self.assertRaisesRegex(RuntimeError, "not idle"):
            self.ns["verified_existing"](self.target, self.task, "credential-id", self.desired)

    def test_creates_replacement_target_and_preserves_settings(self):
        new_id, created = self.ns["ensure_new_target"](self.gmp, ET.Element("get_targets_response"), self.target, "credential-id", self.desired)
        self.assertEqual((new_id, created), ("new-target", True))
        request = self.requests[0]
        self.assertEqual(request.tag, "create_target")
        self.assertEqual(set(request.findtext("hosts").split(",")), self.desired)
        self.assertEqual(request.findtext("exclude_hosts"), "192.168.2.254")
        self.assertEqual(request.find("ssh_credential").get("id"), "credential-id")
        self.assertEqual(request.find("port_list").get("id"), "port-list-id")

    def test_creates_replacement_task_with_existing_scan_config(self):
        task_id, created = self.ns["ensure_new_task"](self.gmp, ET.Element("get_tasks_response"), self.task, "new-target")
        self.assertEqual((task_id, created), ("new-task", True))
        request = self.requests[0]
        self.assertEqual(request.find("target").get("id"), "new-target")
        self.assertEqual(request.find("config").get("id"), "daba56c8-73ec-11df-a475-002264764cea")

    def test_existing_new_target_idempotent(self):
        roots = ET.Element("get_targets_response")
        new = ET.SubElement(roots, "target", {"id": "new-target"})
        ET.SubElement(new, "name").text = self.ns["NEW_TARGET_NAME"]
        ET.SubElement(new, "hosts").text = "192.168.2.48, 192.168.2.1"
        ET.SubElement(new, "ssh_credential", {"id": "credential-id"})
        ET.SubElement(new, "exclude_hosts").text = "192.168.2.254"
        self.assertEqual(
            self.ns["ensure_new_target"](self.gmp, roots, self.target, "credential-id", self.desired),
            ("new-target", False),
        )
        self.assertFalse(self.requests)

    def test_existing_new_target_drift_refused(self):
        roots = ET.Element("get_targets_response")
        new = ET.SubElement(roots, "target", {"id": "new-target"})
        ET.SubElement(new, "name").text = self.ns["NEW_TARGET_NAME"]
        ET.SubElement(new, "hosts").text = "192.168.2.99"
        ET.SubElement(new, "ssh_credential", {"id": "credential-id"})
        with self.assertRaisesRegex(RuntimeError, "drift"):
            self.ns["ensure_new_target"](self.gmp, roots, self.target, "credential-id", self.desired)
        self.assertFalse(self.requests)


if __name__ == "__main__":
    unittest.main()
