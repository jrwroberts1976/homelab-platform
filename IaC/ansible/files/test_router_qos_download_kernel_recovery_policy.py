#!/usr/bin/env python3
"""Offline policy regression tests. No router or kernel commands."""
import unittest
from router_qos_download_kernel_recovery_policy import KernelState, recovery_decision


class RecoveryPolicyTests(unittest.TestCase):
    def state(self, **changes):
        baseline = dict(ppp_present=True, upload_ok=True, ifb_present=False,
                        ifb_verified_owned=False, ingress="clean",
                        owner_record_present=False)
        baseline.update(changes)
        return KernelState(**baseline)

    def test_clean_missing_ifb_is_only_eligible(self):
        self.assertEqual(recovery_decision(self.state()),
                         "CREATE_ONLY_RECOVERY_ELIGIBLE_NOT_AUTHORISED")

    def test_current_legacy_ifb_must_not_be_adopted(self):
        self.assertEqual(recovery_decision(self.state(ifb_present=True, ingress="legacy-exact")),
                         "REFUSE_UNVERIFIED_IFB")

    def test_foreign_ingress_refused(self):
        self.assertEqual(recovery_decision(self.state(ingress="foreign")),
                         "REFUSE_FOREIGN_INGRESS")

    def test_dangling_redirect_refused(self):
        self.assertEqual(recovery_decision(self.state(ingress="legacy-exact")),
                         "REFUSE_DANGLING_REDIRECT")

    def test_stale_owner_record_refused(self):
        self.assertEqual(recovery_decision(self.state(owner_record_present=True)),
                         "REFUSE_STALE_OWNER_RECORD")

    def test_missing_ppp_refused(self):
        self.assertEqual(recovery_decision(self.state(ppp_present=False)),
                         "REFUSE_BASELINE_CHANGED")

    def test_changed_upload_refused(self):
        self.assertEqual(recovery_decision(self.state(upload_ok=False)),
                         "REFUSE_BASELINE_CHANGED")

    def test_verified_owned_working_download_preserved(self):
        self.assertEqual(recovery_decision(self.state(ifb_present=True,
                          ifb_verified_owned=True, ingress="legacy-exact")),
                         "PRESERVE_WORKING_DOWNLOAD")

    def test_owned_ifb_with_clean_ingress_refuses_unsafe_adoption(self):
        self.assertEqual(recovery_decision(self.state(ifb_present=True,
                          ifb_verified_owned=True)), "REFUSE_AMBIGUOUS_OWNED_IFB")

if __name__ == "__main__":
    unittest.main(verbosity=2)
