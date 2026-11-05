"""Offline, fail-closed regression tests for docker-01 to router-01 Greenbone target replacement."""
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "roles/greenbone_scanning/templates/configure-authenticated-scan.py.j2"
MARKER = "{{ 'True' if greenbone_scanning_router_target_approved | default(false) | bool else 'False' }}"


def environment(approved=False):
    raw = TEMPLATE.read_text().split("ROUTER_IP = ", 1)[1].split("def load_runtime_env():", 1)[0]
    source = "ROUTER_IP = " + raw
    assert MARKER in source
    source = source.replace(MARKER, "True" if approved else "False")
    writes = []
    def gmp(xml):
        writes.append(xml)
        return '<modify_target_response status="200"/>'
    ns = {"ET": ET, "HOSTS": "192.168.2.48,192.168.2.52,192.168.2.1", "gmp": gmp}
    exec(compile(source, str(TEMPLATE), "exec"), ns)
    return ns["reconcile_router_host"], writes


def target(hosts, credential="correct"):
    root = ET.Element("target", id="existing-target")
    ET.SubElement(root, "hosts").text = hosts
    ET.SubElement(root, "ssh_credential", id=credential)
    return root


class RouterTargetTests(unittest.TestCase):
    def test_requires_approval(self):
        reconcile, writes = environment()
        with self.assertRaisesRegex(RuntimeError, "approval"):
            reconcile(target("192.168.2.48,192.168.2.52,192.168.2.220"), "correct")
        self.assertFalse(writes)

    def test_approved_replaces_retired_docker_only(self):
        reconcile, writes = environment(True)
        self.assertEqual(reconcile(target("192.168.2.48,192.168.2.52,192.168.2.220"), "correct"), ("existing-target", True))
        self.assertEqual(len(writes), 1)
        xml = ET.fromstring(writes[0])
        self.assertEqual(xml.tag, "modify_target")
        self.assertEqual(xml.get("target_id"), "existing-target")
        self.assertEqual(set(xml.findtext("hosts").split(",")), {"192.168.2.48", "192.168.2.52", "192.168.2.1"})

    def test_idempotent(self):
        reconcile, writes = environment()
        self.assertEqual(reconcile(target("192.168.2.1,192.168.2.52,192.168.2.48"), "correct"), ("existing-target", False))
        self.assertFalse(writes)

    def test_refuses_addition_without_retired_ip(self):
        reconcile, writes = environment(True)
        with self.assertRaisesRegex(RuntimeError, "drift"):
            reconcile(target("192.168.2.48,192.168.2.52"), "correct")
        self.assertFalse(writes)

    def test_rejects_unexpected_drift(self):
        reconcile, writes = environment(True)
        with self.assertRaisesRegex(RuntimeError, "drift"):
            reconcile(target("192.168.2.48"), "correct")
        self.assertFalse(writes)

    def test_refuses_unexpected_extra_host(self):
        reconcile, writes = environment(True)
        with self.assertRaisesRegex(RuntimeError, "drift"):
            reconcile(target("192.168.2.48,192.168.2.52,192.168.2.220,192.168.2.99"), "correct")
        self.assertFalse(writes)

    def test_rejects_wrong_credential(self):
        reconcile, writes = environment(True)
        with self.assertRaisesRegex(RuntimeError, "credential"):
            reconcile(target("192.168.2.48,192.168.2.52,192.168.2.220", "wrong"), "correct")
        self.assertFalse(writes)

    def test_refuses_retired_ip_in_desired_inventory(self):
        reconcile, writes = environment(True)
        reconcile.__globals__["HOSTS"] += ",192.168.2.220"
        with self.assertRaisesRegex(RuntimeError, "drift"):
            reconcile(target("192.168.2.48,192.168.2.52,192.168.2.220"), "correct")
        self.assertFalse(writes)

    def test_rejects_duplicate_target_hosts(self):
        reconcile, writes = environment(True)
        with self.assertRaisesRegex(RuntimeError, "Duplicate"):
            reconcile(target("192.168.2.48,192.168.2.48"), "correct")
        self.assertFalse(writes)


if __name__ == "__main__":
    unittest.main()
