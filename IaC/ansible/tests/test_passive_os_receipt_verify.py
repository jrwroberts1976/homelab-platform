#!/usr/bin/env python3
"""Offline local receipt integrity protocol tests; no network or SSH."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(ROOT))
from passive_os_batch_spool import prepare
from passive_os_batch_receiver import receive
from passive_os_receipt_verify import verify


class ReceiptVerifierTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        base = Path(t.name)
        self.spool = base / 'spool'
        self.received = base / 'received'
        eve = base / 'eve.json'
        event = {'event_type': 'http',
                 'timestamp': '2026-11-06T12:00:00Z',
                 'src_ip': '192.168.2.113',
                 'http': {'http_user_agent': 'Mozilla/5.0 (X11; CrOS x86_64 1)'}}
        eve.write_text(json.dumps(event) + '\n')
        self.batch = prepare(eve, self.spool)
        self.pending = self.spool / 'pending.json'
        receive(self.pending, self.received)
        ident = self.batch['batch_id']
        self.stored = self.received / (ident + '.json')
        self.receipt = self.received / (ident + '.receipt.json')

    def test_valid_pair_is_locally_verified(self):
        result = verify(self.pending, self.stored, self.receipt)
        self.assertEqual(result['status'], 'locally_verified')
        self.assertEqual(result['batch_id'], self.batch['batch_id'])

    def test_interrupted_transfer_missing_stored_file_rejected(self):
        self.stored.unlink()
        with self.assertRaises(FileNotFoundError):
            verify(self.pending, self.stored, self.receipt)

    def test_interrupted_transfer_missing_receipt_rejected(self):
        self.receipt.unlink()
        with self.assertRaises(FileNotFoundError):
            verify(self.pending, self.stored, self.receipt)

    def test_truncated_stored_file_rejected(self):
        self.stored.write_bytes(self.stored.read_bytes()[:20])
        with self.assertRaises(ValueError):
            verify(self.pending, self.stored, self.receipt)

    def test_changed_stored_file_rejected(self):
        data = self.stored.read_bytes()
        self.stored.write_bytes(data[:-2] + b'x\n')
        with self.assertRaises(ValueError):
            verify(self.pending, self.stored, self.receipt)

    def test_wrong_receipt_id_rejected(self):
        data = json.loads(self.receipt.read_text())
        data['batch_id'] = '0' * 64
        self.receipt.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            verify(self.pending, self.stored, self.receipt)

    def test_wrong_receipt_digest_rejected(self):
        data = json.loads(self.receipt.read_text())
        data['digest'] = '0' * 64
        self.receipt.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            verify(self.pending, self.stored, self.receipt)

    def test_symlinked_stored_batch_rejected(self):
        original = self.stored.with_suffix('.other')
        self.stored.rename(original)
        self.stored.symlink_to(original)
        with self.assertRaises(ValueError):
            verify(self.pending, self.stored, self.receipt)


if __name__ == '__main__':
    unittest.main()
