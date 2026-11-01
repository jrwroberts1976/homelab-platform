#!/usr/bin/env python3
"""Full offline ownership-record -> kernel observation -> reconnect review tests."""
import tempfile
import unittest
from pathlib import Path
from router_qos_download_owner_record import write_new
from router_qos_download_recovery_review import review_reconnect

BOOT = "11111111-2222-3333-4444-555555555555"
TOKEN = "0123456789abcdef0123456789abcdef"

class RecoveryReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.owner_file = Path(self.temp.name) / "owner.json"
        self.owner = dict(boot_id=BOOT, ifb_name="ifbqosdl0", ifb_ifindex=17, token=TOKEN)
        write_new(self.owner_file, self.owner)
        self.current = dict(event="up", interface="ppp0", ppp_ifindex=7, old_session_confirmed_gone=True)
        self.previous = dict(interface="ppp0", ppp_ifindex=5)
        self.outputs = {
            ("ip","-j","link","show","dev","ifbqosdl0"): '[{"ifname":"ifbqosdl0","ifindex":17,"ifalias":"router-qos-download:'+TOKEN+'"}]',
            ("ip","-j","link","show","dev","ppp0"): '[{"ifname":"ppp0","ifindex":7}]',
            ("tc","qdisc","show","dev","ifbqosdl0"): "qdisc cake 8009: root bandwidth 43Mbit besteffort flows\n",
            ("tc","qdisc","show","dev","eth1"): "qdisc cake 8001: root bandwidth 13Mbit\n",
            ("tc","filter","show","dev","ppp0","ingress"): "",
            ("tc","qdisc","show","dev","ppp0"): "qdisc noqueue 0: root\n",
        }
        self.paths = {"/proc/sys/kernel/random/boot_id": BOOT,
                      "/sys/class/net/ifbqosdl0/ifindex": "17"}
        self.commands = []

    def review(self, verified=False, current=None, previous="default"):
        def run(argv):
            self.commands.append(tuple(argv))
            return self.outputs.get(tuple(argv), "")
        def read(path):
            return self.paths.get(path, "")
        prev = self.previous if previous == "default" else previous
        return review_reconnect(self.owner_file, self.current if current is None else current,
                                prev, run, read, verified)

    def test_matching_chain_only_proposes(self):
        self.assertEqual(self.review().decision, "cleanup_proposed")
        self.assertTrue(all(x[0] in ("ip", "tc") for x in self.commands))
        self.assertTrue(all("del" not in x and "add" not in x for x in self.commands))

    def test_unknown_other_users_refused(self):
        self.assertEqual(self.review(verified=None).decision, "preserve")

    def test_missing_record_refused(self):
        self.owner_file.unlink()
        self.assertEqual(self.review().decision, "preserve")

    def test_corrupt_record_refused(self):
        self.owner_file.write_text("{")
        self.assertEqual(self.review().decision, "preserve")

    def test_stale_record_boot_refused(self):
        self.paths["/proc/sys/kernel/random/boot_id"] = "00000000-2222-3333-4444-555555555555"
        self.assertEqual(self.review().decision, "preserve")

    def test_changed_ifb_index_refused(self):
        self.paths["/sys/class/net/ifbqosdl0/ifindex"] = "19"
        self.assertEqual(self.review().decision, "preserve")

    def test_unverified_previous_session_refused(self):
        self.assertEqual(self.review(previous=None).decision, "preserve")

    def test_caller_cannot_forge_kernel(self):
        fake = dict(self.current, kernel=dict(self.owner, other_ifb_users=False))
        self.outputs[("ip","-j","link","show","dev","ifbqosdl0")] = "[]"
        self.assertEqual(self.review(current=fake).decision, "preserve")

    def test_unknown_filter_refused(self):
        self.outputs[("tc","filter","show","dev","ppp0","ingress")] = "foreign"
        self.assertEqual(self.review().decision, "preserve")

    def test_changed_upload_refused(self):
        self.outputs[("tc","qdisc","show","dev","eth1")] = "qdisc fq_codel 0: root"
        self.assertEqual(self.review().decision, "preserve")

if __name__ == "__main__":
    unittest.main(verbosity=2)
