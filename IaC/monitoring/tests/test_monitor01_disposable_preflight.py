"""Offline safety tests for the read-only disposable-pair admission script."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "drills/monitor01_disposable_preflight.py"
spec = importlib.util.spec_from_file_location("disposable_admission", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def guest(name, ip, machine_id):
    return {
        "hostname": name,
        "machine_id": machine_id,
        "interfaces": ('[{"ifname":"eth0","addr_info":'
                       '[{"family":"inet","local":"' + ip + '"}]},'
                       '{"ifname":"lo","addr_info":'
                       '[{"family":"inet","local":"127.0.0.1"}]}]'),
        "routes": '[{"dst":"10.77.77.0/24","dev":"eth0"}]',
        "systemd": "systemd 257",
    }


class DisposableAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.source = guest("drill-source", "10.77.77.11", "a" * 32)
        self.target = guest("drill-target", "10.77.77.12", "b" * 32)

    def test_admits_unique_guests_on_isolated_bridge(self):
        self.assertNotEqual(
            module.validate_guest("drill-source", "10.77.77.11", self.source),
            module.validate_guest("drill-target", "10.77.77.12", self.target))

    def test_rejects_both_real_production_addresses(self):
        for addr in ("192.168.2.71", "192.168.2.52", "192.168.2.48"):
            with self.subTest(addr=addr), self.assertRaises(ValueError):
                module.check_candidate(addr)

    def test_rejects_default_route_or_prod_route(self):
        for routes in ([{"dst": "default", "gateway": "10.77.77.1"}],
                       [{"dst": "192.168.2.0/24", "dev": "eth1"}],
                       [{"dst": "192.168.0.0/16", "dev": "eth1"}],
                       [{"dst": "10.42.0.0/16", "gateway": "10.42.0.1"}]):
            with self.subTest(routes=routes), self.assertRaises(ValueError):
                module.validate_routes(routes)

    def test_rejects_real_hostnames(self):
        self.source["hostname"] = "Proxmox-2"
        with self.assertRaises(ValueError):
            module.validate_guest("drill-source", "10.77.77.11", self.source)

    def test_rejects_extra_production_interface(self):
        import json
        interfaces = json.loads(self.source["interfaces"])
        interfaces.append({"ifname": "eth1", "addr_info": [
            {"family": "inet", "local": "192.168.2.71"}]})
        self.source["interfaces"] = json.dumps(interfaces)
        with self.assertRaises(ValueError):
            module.validate_guest("drill-source", "10.77.77.11", self.source)

    def test_rejects_missing_guest_address(self):
        with self.assertRaises(ValueError):
            module.validate_guest("drill-source", "10.77.77.99", self.source)

    def test_rejects_nonsystemd_guest(self):
        self.source["systemd"] = "OpenRC 0.56"
        with self.assertRaises(ValueError):
            module.validate_guest("drill-source", "10.77.77.11", self.source)

    def test_rejects_invalid_machine_id(self):
        self.source["machine_id"] = ""
        with self.assertRaises(ValueError):
            module.validate_guest("drill-source", "10.77.77.11", self.source)

    def test_rejects_duplicate_or_nonlab_endpoints_before_ssh(self):
        for args in (["--source", "10.77.77.11", "--target", "10.77.77.11"],
                     ["--source", "192.168.2.71", "--target", "10.77.77.12"],
                     ["--source", "10.77.77.11", "--target", "192.168.2.52"]):
            with self.subTest(args=args):
                self.assertEqual(module.main(args), 1)


if __name__ == "__main__":
    unittest.main()
