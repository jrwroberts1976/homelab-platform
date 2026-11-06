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

    def test_unsafe_destination_rejected(self):
        self.dest.mkdir()
        self.dest.chmod(0o755)
        with self.assertRaises(ValueError):
            receive(self.pending, self.dest)


if __name__ == '__main__':
    unittest.main()
