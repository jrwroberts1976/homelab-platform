#!/usr/bin/env python3
"""Offline negative/positive ownership decisions; no networking or privileges."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).with_name("router_qos_download_ownership.py")
spec = importlib.util.spec_from_file_location("router_qos_download_ownership", path)
import sys
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

BOOT = "11111111-2222-3333-4444-555555555555"
TOKEN = "0123456789abcdef0123456789abcdef"


class OwnershipTests(unittest.TestCase):
    def setUp(self):
        self.owner = dict(boot_id=BOOT, ifb_name="ifbqosdl0", ifb_ifindex=17, token=TOKEN)
        self.actual = dict(boot_id=BOOT, ifb_name="ifbqosdl0", ifb_ifindex=17,
                           kernel_alias_token=TOKEN, qdisc="cake-43mbit-besteffort-flows",
                           ppp_present=True, ppp_ingress="clean", upload="cake-13mbit",
                           other_ifb_users=False)

    def outcome(self, owner=None, actual=None):
        return module.decide(self.owner if owner is None else owner,
                             self.actual if actual is None else actual).action

    def test_exact_match_proposes_not_executes(self):
        self.assertEqual(self.outcome(), "cleanup_proposed")

    def test_missing_record(self):
        self.assertEqual(module.decide(None, self.actual).action, "preserve")

    def test_stale_boot(self):
        self.assertEqual(self.outcome(actual=dict(self.actual, boot_id="00000000-2222-3333-4444-555555555555")), "preserve")

    def test_reused_ifindex(self):
        self.assertEqual(self.outcome(actual=dict(self.actual, ifb_ifindex=19)), "preserve")

    def test_kernel_token_mismatch(self):
        self.assertEqual(self.outcome(actual=dict(self.actual, kernel_alias_token="f" * 32)), "preserve")

    def test_foreign_qdisc(self):
        self.assertEqual(self.outcome(actual=dict(self.actual, qdisc="fq_codel")), "preserve")

    def test_ppp_not_clean(self):
        self.assertEqual(self.outcome(actual=dict(self.actual, ppp_ingress="foreign")), "preserve")

    def test_ppp_absent(self):
        self.assertEqual(self.outcome(actual=dict(self.actual, ppp_present=False)), "preserve")

    def test_upload_changed(self):
        self.assertEqual(self.outcome(actual=dict(self.actual, upload="fq_codel")), "preserve")

    def test_other_users_unknown(self):
        self.assertEqual(self.outcome(actual=dict(self.actual, other_ifb_users=None)), "preserve")

    def test_record_extra_field(self):
        self.assertEqual(self.outcome(owner=dict(self.owner, externally_verified=True)), "preserve")

    def test_invalid_record(self):
        self.assertEqual(self.outcome(owner=dict(self.owner, ifb_ifindex=True)), "preserve")


if __name__ == "__main__":
    unittest.main(verbosity=2)
