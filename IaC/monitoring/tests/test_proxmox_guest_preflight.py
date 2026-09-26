"""Offline security/identity tests for the read-only Proxmox guest probe."""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "ansible/roles/network_host_enrichment/files/proxmox-guest-preflight.py"
spec = importlib.util.spec_from_file_location("proxmox_guest_preflight", SCRIPT)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def fake_fetch(*, duplicate=False, config_failure=False, inconsistent=False):
    guests = [
        {"type": "qemu", "vmid": 200, "node": "PROXMOX",
         "status": "running", "name": "cloud-01", "template": 0},
        {"type": "lxc", "vmid": 101, "node": "Proxmox-2",
         "status": "running", "name": "dns-01", "template": 0},
        {"type": "qemu", "vmid": 201, "node": "PROXMOX",
         "status": "running", "name": "sensor-01", "template": 0},
        {"type": "qemu", "vmid": 9000, "node": "PROXMOX",
         "status": "stopped", "name": "template", "template": 1},
    ]
    configs = {
        ("PROXMOX", "qemu", 200): {
            "net0": "virtio=BC:24:11:AA:00:01,bridge=vmbr0"},
        ("Proxmox-2", "lxc", 101): {
            "net0": "name=eth0,bridge=vmbr0,hwaddr=52:54:00:00:00:02,type=veth"},
        ("PROXMOX", "qemu", 201): {
            "net0": "e1000=DE:AD:BE:EF:00:03,bridge=vmbr0"},
        ("PROXMOX", "qemu", 9000): {
            "net0": "virtio=BC:24:11:AA:00:01,bridge=vmbr0"},
    }
    if duplicate:
        configs[("PROXMOX", "qemu", 201)] = {
            "net0": "virtio=BC:24:11:AA:00:01,bridge=vmbr0"}
    if config_failure:
        configs[("Proxmox-2", "lxc", 101)] = {
            "net0": "name=eth0,bridge=vmbr0,type=veth"}

    def fetch(node, endpoint):
        if endpoint == "/cluster/resources?type=vm":
            if inconsistent and node == "Proxmox-2":
                return guests[:-1]
            return guests
        _, _, _, host, kind, vmid, _ = endpoint.split("/")
        return configs[(host, kind, int(vmid))]

    return fetch


class GuestProbeTests(unittest.TestCase):
    def test_qemu_mac_extraction(self):
        self.assertEqual(probe.parse_nics(
            "qemu", {"net0": "virtio=BC:24:11:AA:00:01,bridge=vmbr0"}
        ), ["bc:24:11:aa:00:01"])

    def test_lxc_mac_extraction(self):
        self.assertEqual(probe.parse_nics(
            "lxc", {"net0": "name=eth0,bridge=vmbr0,hwaddr=52:54:00:00:00:02"}
        ), ["52:54:00:00:00:02"])

    def test_no_identity_leak_in_summary_and_templates_excluded(self):
        summary = probe.collect(fake_fetch())
        self.assertEqual(summary["cluster_resources"], 4)
        self.assertEqual(summary["guest_configs_checked"], 4)
        self.assertEqual(summary["templates_excluded"], 1)
        self.assertEqual(summary["unique_guest_macs"], 3)
        self.assertFalse(summary["writes"])
        self.assertNotIn("mac_to_guest", summary)

    def test_duplicate_mac_refused(self):
        with self.assertRaisesRegex(ValueError, "share one MAC"):
            probe.collect(fake_fetch(duplicate=True))

    def test_unreadable_running_mac_refused(self):
        with self.assertRaisesRegex(ValueError, "missing/ambiguous MAC"):
            probe.collect(fake_fetch(config_failure=True))

    def test_inconsistent_nodes_refused(self):
        with self.assertRaisesRegex(ValueError, "agree"):
            probe.collect(fake_fetch(inconsistent=True))

    def test_unknown_node_refused(self):
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            probe.get_json(
                "unknown", "/cluster/resources?type=vm", "secret", None,
            )

    def test_invalid_mac_refused(self):
        with self.assertRaisesRegex(ValueError, "invalid MAC"):
            probe.parse_nics("qemu", {
                "net0": "virtio=BC:24:11:AA:00:ZZ,bridge=vmbr0"})

    def test_no_arbitrary_text_mac_extraction(self):
        with self.assertRaisesRegex(ValueError, "missing/ambiguous MAC"):
            probe.parse_nics("qemu", {
                "net0": "name=BC:24:11:AA:00:01,bridge=vmbr0"})


if __name__ == "__main__":
    unittest.main()
