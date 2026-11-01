#!/usr/bin/env python3
"""Offline observations wired to ownership and reconnect gates; no host access."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from router_qos_download_observe import observe
from router_qos_download_reconnect_gate import plan_reconnect

BOOT="11111111-2222-3333-4444-555555555555"
TOKEN="0123456789abcdef0123456789abcdef"


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.outputs = {
            ("ip","-j","link","show","dev","ifbqosdl0"):
              '[{"ifname":"ifbqosdl0","ifindex":17,"ifalias":"router-qos-download:'+TOKEN+'"}]',
            ("ip","-j","link","show","dev","ppp0"): '[{"ifname":"ppp0","ifindex":7}]',
            ("tc","qdisc","show","dev","ifbqosdl0"):
              "qdisc cake 8009: root bandwidth 43Mbit besteffort flows\n",
            ("tc","qdisc","show","dev","eth1"):
              "qdisc cake 8001: root bandwidth 13Mbit besteffort flows\n",
            ("tc","filter","show","dev","ppp0","ingress"): "",
            ("tc","qdisc","show","dev","ppp0"): "qdisc noqueue 0: root\n",
        }
        self.paths = {
            "/proc/sys/kernel/random/boot_id": BOOT,
            "/sys/class/net/ifbqosdl0/ifindex": "17",
        }
        self.owner = dict(boot_id=BOOT,ifb_name="ifbqosdl0",ifb_ifindex=17,token=TOKEN)

    def snapshot(self, other_users=False):
        return observe(lambda args:self.outputs.get(tuple(args), ""),
                       lambda path:self.paths.get(path, ""),other_users)

    def decision(self, other_users=False):
        return plan_reconnect(self.owner, dict(event="up", interface="ppp0", ppp_ifindex=7,
              old_session_confirmed_gone=True,kernel=self.snapshot(other_users)),
              dict(interface="ppp0",ppp_ifindex=5)).decision

    def test_valid_evidence_proposes_only(self):
        self.assertEqual(self.decision(), "cleanup_proposed")
    def test_unknown_other_users_refuses(self):
        self.assertEqual(self.decision(None), "preserve")
    def test_foreign_filter_refuses(self):
        self.outputs[("tc","filter","show","dev","ppp0","ingress")] = "filter pref 99 foreign"
        self.assertEqual(self.decision(), "preserve")
    def test_clsact_not_clean(self):
        self.outputs[("tc","qdisc","show","dev","ppp0")] = "qdisc clsact ffff: parent ffff:fff1"
        self.assertEqual(self.decision(), "preserve")
    def test_missing_ifb_alias_refuses(self):
        self.outputs[("ip","-j","link","show","dev","ifbqosdl0")] = '[{"ifname":"ifbqosdl0","ifindex":17}]'
        self.assertEqual(self.decision(), "preserve")
    def test_missing_ifb_ifindex_refuses(self):
        self.paths["/sys/class/net/ifbqosdl0/ifindex"]=""
        self.assertEqual(self.decision(), "preserve")
    def test_unknown_cake_refuses(self):
        self.outputs[("tc","qdisc","show","dev","ifbqosdl0")]="qdisc fq_codel 0: root"
        self.assertEqual(self.decision(), "preserve")
    def test_changed_upload_refuses(self):
        self.outputs[("tc","qdisc","show","dev","eth1")]="qdisc fq_codel 0: root"
        self.assertEqual(self.decision(), "preserve")
    def test_stale_boot_refuses(self):
        self.paths["/proc/sys/kernel/random/boot_id"]="00000000-2222-3333-4444-555555555555"
        self.assertEqual(self.decision(), "preserve")


if __name__ == "__main__":
    unittest.main(verbosity=2)
