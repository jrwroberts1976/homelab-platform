#!/usr/bin/env python3
"""Pure tests for parallel IFB ownership compatibility, no system calls."""
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
from router_qos_download_owner_stamp import stamp_new_ifb
from router_qos_download_owner_record import load, validate_record
from router_qos_download_ownership import decide
from router_qos_download_observe import observe

BOOT = "11111111-2222-3333-4444-555555555555"
TOKEN = "a" * 32

class ParallelIFBTests(unittest.TestCase):
    def test_candidate_record_schema(self):
        validate_record(dict(boot_id=BOOT, ifb_name="ifbqosdl1", ifb_ifindex=99, token=TOKEN))

    def test_unknown_interface_rejected(self):
        with self.assertRaises(ValueError):
            validate_record(dict(boot_id=BOOT, ifb_name="ifbother", ifb_ifindex=99, token=TOKEN))

    def test_new_candidate_stamped_without_legacy_adoption(self):
        with tempfile.TemporaryDirectory() as directory:
            alias = [""]
            with patch("router_qos_download_owner_stamp.secrets.token_hex", return_value=TOKEN):
                stamp_new_ifb(Path(directory)/"owner", BOOT, lambda: 99,
                              lambda: alias[0], lambda a: alias.__setitem__(0, a),
                              ifb_name="ifbqosdl1")
            self.assertEqual(load(Path(directory)/"owner")["ifb_name"], "ifbqosdl1")
            self.assertEqual(alias[0], "router-qos-download:"+TOKEN)

    def test_unknown_stamp_target_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                stamp_new_ifb(Path(directory)/"owner", BOOT, lambda: 99,
                              lambda: "", lambda _: None, ifb_name="eth1")

    def test_candidate_ownership_match_requires_clean_ingress(self):
        owner = dict(boot_id=BOOT, ifb_name="ifbqosdl1", ifb_ifindex=99, token=TOKEN)
        observed = dict(boot_id=BOOT, ifb_name="ifbqosdl1", ifb_ifindex=99,
                        kernel_alias_token=TOKEN, qdisc="cake-43mbit-besteffort-flows",
                        ppp_present=True, ppp_ingress="clean", upload="cake-13mbit",
                        other_ifb_users=False)
        self.assertEqual(decide(owner, observed).action, "cleanup_proposed")
        observed["other_ifb_users"] = None
        self.assertEqual(decide(owner, observed).action, "preserve")

    def test_observer_uses_candidate_interface_without_network(self):
        commands = []
        def run(args):
            commands.append(args)
            if args[:3] == ["ip", "-j", "link"]:
                return '[{"ifname":"'+args[-1]+'","ifalias":"router-qos-download:'+TOKEN+'"}]'
            if args[:3] == ["tc", "qdisc", "show"] and args[-1] == "ifbqosdl1":
                return "qdisc cake 1: root bandwidth 43Mbit besteffort flows"
            if args[:3] == ["tc", "qdisc", "show"] and args[-1] == "eth1":
                return "qdisc cake root bandwidth 13Mbit"
            return ""
        def read(path):
            return BOOT if path.endswith("boot_id") else "99"
        result = observe(run, read, ifb_name="ifbqosdl1")
        self.assertEqual(result["ifb_name"], "ifbqosdl1")
        self.assertTrue(any(cmd[-1] == "ifbqosdl1" for cmd in commands))
        self.assertFalse(any(cmd[-1] == "ifbqosdl0" for cmd in commands))

if __name__ == "__main__":
    unittest.main(verbosity=2)
