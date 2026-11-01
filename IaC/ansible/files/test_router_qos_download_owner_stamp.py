#!/usr/bin/env python3
"""Offline tests for install-only IFB ownership stamp. No router access."""
import tempfile
import unittest
from pathlib import Path
from router_qos_download_owner_stamp import stamp_new_ifb

BOOT="11111111-2222-3333-4444-555555555555"

class StampTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"owner.json"
        self.ifindex=17
        self.alias=""
        self.writes=[]

    def stamp(self):
        def set_alias(value):
            self.writes.append(value)
            self.alias=value
        return stamp_new_ifb(self.path,BOOT,lambda:self.ifindex,
                             lambda:self.alias,set_alias)

    def test_new_object_stamped_and_recorded(self):
        record=self.stamp()
        self.assertEqual(record["ifb_ifindex"],17)
        self.assertEqual(self.alias,"router-qos-download:"+record["token"])
        self.assertTrue(self.path.is_file())

    def test_existing_record_refused_without_kernel_change(self):
        self.stamp()
        before=list(self.writes)
        with self.assertRaises(FileExistsError): self.stamp()
        self.assertEqual(self.writes,before)

    def test_existing_kernel_alias_refused(self):
        self.alias="foreign"
        with self.assertRaises(ValueError): self.stamp()
        self.assertFalse(self.writes)
        self.assertFalse(self.path.exists())

    def test_invalid_index_refused(self):
        self.ifindex=0
        with self.assertRaises(ValueError): self.stamp()
        self.assertFalse(self.writes)

    def test_symlink_record_refused(self):
        target=Path(self.tmp.name)/"foreign"
        target.write_text("unchanged")
        self.path.symlink_to(target)
        with self.assertRaises(FileExistsError): self.stamp()
        self.assertEqual(target.read_text(),"unchanged")
        self.assertFalse(self.writes)

    def test_changed_index_after_stamp_refused(self):
        def set_alias(value):
            self.alias=value
            self.ifindex=22
        with self.assertRaises(RuntimeError):
            stamp_new_ifb(self.path,BOOT,lambda:self.ifindex,lambda:self.alias,set_alias)
        self.assertFalse(self.path.exists())

if __name__=="__main__":
    unittest.main(verbosity=2)
