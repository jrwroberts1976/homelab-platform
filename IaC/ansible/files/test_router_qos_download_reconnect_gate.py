#!/usr/bin/env python3
"""Offline integration tests: PPP lifecycle + kernel ownership, no networking."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from router_qos_download_reconnect_gate import plan_reconnect

BOOT="11111111-2222-3333-4444-555555555555"
TOKEN="0123456789abcdef0123456789abcdef"

class ReconnectIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.owner=dict(boot_id=BOOT, ifb_name="ifbqosdl0", ifb_ifindex=17, token=TOKEN)
        self.old=dict(interface="ppp0", ppp_ifindex=5)
        kernel=dict(boot_id=BOOT, ifb_name="ifbqosdl0", ifb_ifindex=17,
                    kernel_alias_token=TOKEN, qdisc="cake-43mbit-besteffort-flows",
                    ppp_present=True, ppp_ingress="clean", upload="cake-13mbit",
                    other_ifb_users=False)
        self.current=dict(event="up", interface="ppp0", ppp_ifindex=7,
                          old_session_confirmed_gone=True, kernel=kernel)

    def check(self, expected, owner=None, current=None, old=None):
        result=plan_reconnect(self.owner if owner is None else owner,
                              self.current if current is None else current,
                              self.old if old is None else old)
        self.assertEqual(result.decision, expected, result.reason)

    def test_good_reconnect_proposes_only(self): self.check("cleanup_proposed")
    def test_duplicate_up_preserves(self):
        self.check("preserve", old=dict(self.old, ppp_ifindex=7))
    def test_old_session_not_gone(self):
        self.check("preserve", current=dict(self.current, old_session_confirmed_gone=False))
    def test_stale_boot_preserves(self):
        self.check("preserve", current=dict(self.current, kernel=dict(self.current["kernel"], boot_id="0"*8+"-2222-3333-4444-555555555555")))
    def test_replaced_ifb_preserves(self):
        self.check("preserve", current=dict(self.current, kernel=dict(self.current["kernel"], ifb_ifindex=99)))
    def test_foreign_filter_preserves(self):
        self.check("preserve", current=dict(self.current, kernel=dict(self.current["kernel"], ppp_ingress="foreign")))
    def test_unknown_ifb_users_preserves(self):
        self.check("preserve", current=dict(self.current, kernel=dict(self.current["kernel"], other_ifb_users=None)))
    def test_token_mismatch_preserves(self):
        self.check("preserve", current=dict(self.current, kernel=dict(self.current["kernel"], kernel_alias_token="f"*32)))
    def test_unmanaged_event_ignored(self):
        self.check("ignore", current=dict(self.current, interface="ppp1"))
    def test_missing_previous_session_preserves(self):
        self.assertEqual(plan_reconnect(self.owner, self.current, None).decision, "preserve")
    def test_missing_record_preserves(self):
        self.assertEqual(plan_reconnect(None, self.current, self.old).decision, "preserve")
    def test_partial_install_preserves(self):
        self.check("preserve", current=dict(self.current, kernel=dict(self.current["kernel"], qdisc="none")))

if __name__=="__main__":
    unittest.main(verbosity=2)
