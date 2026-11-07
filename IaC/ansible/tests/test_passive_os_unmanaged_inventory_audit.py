#!/usr/bin/env python3
"""No-network unit tests for existing inventory vs Zabbix OS facts."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from passive_os_unmanaged_inventory_audit import compare


class UnmanagedInventoryTests(unittest.TestCase):
    def setUp(self):
        self.inventory = {
            "192.168.2.1": {"hostname": "router-01.jameshouse"},
            "192.168.2.130": {"hostname": "livingroom-tv"},
            "192.168.2.55": {"hostname": "sensor-01.jameshouse"},
        }
        self.hosts = [
            {"hostid": "10", "host": "router-01", "status": "0",
             "interfaces": []},
            {"hostid": "11", "host": "sensor-01", "status": "0",
             "interfaces": [{"ip": "192.168.2.55", "useip": "1"}]},
        ]
        self.items = [
            {"hostid": "10", "key_": "system.sw.os[name]", "status": "0",
             "state": "0", "lastclock": "1794000000", "lastvalue": "Linux"},
            {"hostid": "11", "key_": "system.sw.os.get", "status": "0",
             "state": "0", "lastclock": "1794000000", "lastvalue": "Linux"},
        ]

    def test_known_os_excluded_from_unmatched(self):
        result = compare(self.inventory, self.hosts, self.items)
        self.assertEqual(len(result["zabbix_os_authoritative"]), 2)
        self.assertEqual(result["unmatched_inventory"], ["192.168.2.130"])

    def test_registered_without_os_not_called_unmanaged(self):
        result = compare(self.inventory, self.hosts, self.items[:1])
        self.assertEqual(result["zabbix_without_os"], ["192.168.2.55"])

    def test_duplicate_identity_remains_ambiguous(self):
        extra = {"hostid": "12", "host": "router-01", "status": "0",
                 "interfaces": []}
        result = compare(self.inventory, self.hosts + [extra], self.items)
        self.assertEqual(result["ambiguous"], ["192.168.2.1"])

    def test_disabled_os_host_not_authoritative(self):
        hosts = [dict(self.hosts[0], status="1")]
        result = compare({"192.168.2.1": self.inventory["192.168.2.1"]},
                         hosts, self.items)
        self.assertEqual(result["unmatched_inventory"], ["192.168.2.1"])

    def test_unsupported_os_not_authoritative(self):
        items = [dict(self.items[0], state="1")]
        result = compare({"192.168.2.1": self.inventory["192.168.2.1"]},
                         self.hosts, items)
        self.assertEqual(result["zabbix_without_os"], ["192.168.2.1"])


if __name__ == "__main__":
    unittest.main()
