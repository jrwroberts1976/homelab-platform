"""Offline regressions for the post-cutover whole-LAN and estate audit tools."""
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
import yaml

ROOT = Path(__file__).resolve().parents[2]
SCAN = ROOT / "monitoring/audits/postcutover_network_scan.py"
EVIDENCE = ROOT / "ansible/playbooks/postcutover-estate-evidence.yml"
spec = importlib.util.spec_from_file_location("postcutover_scan", SCAN)
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


class WholeEstateAuditSafetyTests(unittest.TestCase):
    def test_scan_is_fixed_to_owned_lan_and_limited_service_ports(self):
        self.assertEqual(scanner.SUBNET, "192.168.2.0/24")
        self.assertEqual(scanner.TARGET, "james@192.168.2.52")
        ports = [int(x) for x in scanner.PORTS.split(",")]
        self.assertLessEqual(len(ports), 50)
        self.assertEqual(len(ports), len(set(ports)))
        self.assertTrue(all(1 <= p <= 65535 for p in ports))
        source = SCAN.read_text()
        self.assertIn("--max-rate", source)
        self.assertIn("--version-light", source)
        self.assertNotIn("--script", source)

    def test_nmap_xml_extractor_preserves_open_ports_and_device_identity(self):
        raw = '''<?xml version="1.0"?>
<nmaprun><host><status state="up"/>
<address addr="192.168.2.52" addrtype="ipv4"/>
<address addr="02:00:00:00:02:52" addrtype="mac"/>
<ports><port protocol="tcp" portid="9090"><state state="open"/>
<service name="http" product="Prometheus" version="v1"/></port></ports>
</host><host><status state="down"/><address addr="192.168.2.99" addrtype="ipv4"/></host></nmaprun>'''
        hosts = scanner.parse_hosts(ET.fromstring(raw))
        self.assertEqual(len(hosts), 1)
        self.assertEqual(hosts[0]["ip"], "192.168.2.52")
        self.assertEqual(hosts[0]["open_ports"][0]["port"], 9090)

    def test_target_playbook_gathers_facts_without_remote_writes(self):
        plays = yaml.safe_load(EVIDENCE.read_text())
        self.assertEqual(len(plays), 1)
        play = plays[0]
        self.assertTrue(play["gather_facts"])
        tasks = play["tasks"]
        for task in tasks:
            is_write = "ansible.builtin.copy" in task or "ansible.builtin.file" in task
            if is_write:
                self.assertEqual(task["delegate_to"], "localhost")
                self.assertFalse(task["become"])
        self.assertIn("audit_output_dir", EVIDENCE.read_text())
        self.assertIn("no_log: true", EVIDENCE.read_text())


if __name__ == "__main__":
    unittest.main()
