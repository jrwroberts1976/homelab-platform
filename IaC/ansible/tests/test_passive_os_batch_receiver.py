#!/usr/bin/env python3
"""Local-only receipt and deduplication tests."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(ROOT))
from passive_os_batch_spool import prepare
from passive_os_batch_receiver import receive


class ReceiverTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.eve = self.root / 'input.json'
        self.spool = self.root / 'spool'
        self.dest = self.root / 'received'
        record = {'timestamp': '2026-11-06T11:00:00Z',
                  'src_ip': '192.168.2.113', 'event_type': 'http',
                  'http': {'http_user_agent': 'CrOS 123'},
                  'http_url': '/sensitive'}
        self.eve.write_text(json.dumps(record) + '\n')
        self.pending = self.spool / 'pending.json'
        self.batch = prepare(self.eve, self.spool)

    def test_first_delivery_creates_receipt(self):
        result = receive(self.pending, self.dest)
        self.assertEqual(result['status'], 'stored')
        self.assertTrue((self.dest / (self.batch['batch_id'] + '.receipt.json')).exists())

    def test_repeated_delivery_is_duplicate(self):
        first = receive(self.pending, self.dest)
        second = receive(self.pending, self.dest)
        self.assertEqual(first['batch_id'], second['batch_id'])
        self.assertEqual(second['status'], 'duplicate')
        self.assertEqual(len(list(self.dest.glob('*.json'))), 2)

    def test_pending_corruption_fails_closed(self):
        data = json.loads(self.pending.read_text())
        data['observations'][0]['os_family_hint'] = 'Android'
        self.pending.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            receive(self.pending, self.dest)

    def test_saved_content_is_minimal_and_private(self):
        result = receive(self.pending, self.dest)
        batch_path = self.dest / (result['batch_id'] + '.json')
        self.assertEqual(batch_path.stat().st_mode & 0o777, 0o600)
        self.assertNotIn('sensitive', batch_path.read_text())

    def test_conflicting_existing_batch_rejected(self):
        first = receive(self.pending, self.dest)
        batch_path = self.dest / (first['batch_id'] + '.json')
        batch_path.write_bytes(b'different')
        with self.assertRaises(ValueError):
            receive(self.pending, self.dest)

    def test_byte_quota_refuses_new_batch(self):
        from unittest.mock import patch
        self.dest.mkdir(mode=0o700)
        with patch('passive_os_batch_receiver.MAX_RETAINED_BYTES', 10):
            with self.assertRaisesRegex(ValueError, 'byte quota'):
                receive(self.pending, self.dest)
        self.assertEqual(list(self.dest.glob('*.json')), [])

    def test_batch_count_quota_refuses_new_batch(self):
        from unittest.mock import patch
        self.dest.mkdir(mode=0o700)
        with patch('passive_os_batch_receiver.MAX_RETAINED_BATCHES', 0):
            with self.assertRaisesRegex(ValueError, 'batch quota'):
                receive(self.pending, self.dest)
        self.assertEqual(list(self.dest.glob('*.json')), [])

    def test_duplicate_delivery_allowed_at_full_capacity(self):
        from unittest.mock import patch
        first = receive(self.pending, self.dest)
        with patch('passive_os_batch_receiver.MAX_RETAINED_BATCHES', 1):
            again = receive(self.pending, self.dest)
        self.assertEqual(first['batch_id'], again['batch_id'])
        self.assertEqual(again['status'], 'duplicate')

    def test_unexpected_files_refuse_new_batch(self):
        self.dest.mkdir(mode=0o700)
        (self.dest / 'unexpected.txt').write_text('unexpected')
        with self.assertRaisesRegex(ValueError, 'Unexpected receiver file'):
            receive(self.pending, self.dest)

    def test_symlink_in_receipt_directory_refused(self):
        self.dest.mkdir(mode=0o700)
        (self.dest / 'badlink').symlink_to(self.pending)
        with self.assertRaisesRegex(ValueError, 'Unsafe receiver'):
            receive(self.pending, self.dest)

    def test_retention_never_automatically_deletes_existing_files(self):
        from unittest.mock import patch
        receive(self.pending, self.dest)
        before = {p.name: p.read_bytes() for p in self.dest.glob('*.json')}
        with patch('passive_os_batch_receiver.MAX_RETAINED_BATCHES', 0):
            with self.assertRaisesRegex(ValueError, 'batch quota'):
                __import__('passive_os_batch_receiver').capacity_check(
                    self.dest, new_batch=True)
        after = {p.name: p.read_bytes() for p in self.dest.glob('*.json')}
        self.assertEqual(before, after)

    def test_unsafe_destination_rejected(self):
        self.dest.mkdir()
        self.dest.chmod(0o755)
        with self.assertRaises(ValueError):
            receive(self.pending, self.dest)


if __name__ == '__main__':
    unittest.main()
