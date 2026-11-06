#!/usr/bin/env python3
"""Offline durable spool protocol tests; no router connections or SSH."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location('passive_os_batch_spool',
                                              ROOT / 'passive_os_batch_spool.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def sample(kind='http'):
    return {'timestamp': '2026-11-06T11:00:00+00:00',
            'src_ip': '192.168.2.113', 'event_type': kind,
            'http': {'http_user_agent': 'Mozilla/5.0 (X11; CrOS x86_64 1)'},
            'url': '/private', 'dns': {'rrname': 'private.example'}}


class SpoolTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        self.eve = base / 'eve.json'
        self.spool = base / 'spool'

    def append(self, events):
        with self.eve.open('ab') as out:
            for event in events:
                out.write((json.dumps(event) + '\n').encode())

    def test_prepare_is_idempotent_without_ack(self):
        self.append([sample(), sample('dns')])
        first = mod.prepare(self.eve, self.spool)
        second = mod.prepare(self.eve, self.spool)
        self.assertEqual(first['status'], 'prepared')
        self.assertEqual(second['status'], 'pending')
        self.assertEqual(first['batch_id'], second['batch_id'])
        self.assertFalse((self.spool / 'checkpoint.json').exists())

    def test_wrong_ack_does_not_advance(self):
        self.append([sample()])
        first = mod.prepare(self.eve, self.spool)
        with self.assertRaises(ValueError):
            mod.ack(self.spool, 'invalid')
        self.assertFalse((self.spool / 'checkpoint.json').exists())
        self.assertTrue((self.spool / 'pending.json').exists())

    def test_ack_advances_and_next_prepare_is_idle(self):
        self.append([sample()])
        first = mod.prepare(self.eve, self.spool)
        self.assertEqual(mod.ack(self.spool, first['batch_id'])['status'],
                         'acknowledged')
        self.assertTrue((self.spool / 'checkpoint.json').exists())
        self.assertFalse((self.spool / 'pending.json').exists())
        self.assertEqual(mod.prepare(self.eve, self.spool)['status'], 'idle')

    def test_next_batch_only_after_ack(self):
        self.append([sample()])
        first = mod.prepare(self.eve, self.spool)
        self.append([sample(kind='tls')])
        blocked = mod.prepare(self.eve, self.spool)
        self.assertEqual(blocked['batch_id'], first['batch_id'])
        mod.ack(self.spool, first['batch_id'])
        next_batch = mod.prepare(self.eve, self.spool)
        self.assertNotEqual(next_batch['batch_id'], first['batch_id'])
        self.assertEqual(next_batch['observations'], 1)

    def test_pending_contains_only_minimised_evidence(self):
        self.append([sample()])
        mod.prepare(self.eve, self.spool)
        content = (self.spool / 'pending.json').read_text()
        self.assertNotIn('private.example', content)
        self.assertNotIn('/private', content)
        self.assertNotIn('Mozilla/', content)
        self.assertIn('ChromeOS', content)

    def test_corrupt_pending_rejected_fail_closed(self):
        self.append([sample()])
        mod.prepare(self.eve, self.spool)
        p = self.spool / 'pending.json'
        data = json.loads(p.read_text())
        data['observations'][0]['os_family_hint'] = 'Windows'
        p.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            mod.prepare(self.eve, self.spool)
        self.assertFalse((self.spool / 'checkpoint.json').exists())

    def test_empty_eve_is_idle(self):
        self.eve.write_bytes(b'')
        self.assertEqual(mod.prepare(self.eve, self.spool)['status'], 'idle')

    def test_private_pending_file_permissions(self):
        self.append([sample()])
        mod.prepare(self.eve, self.spool)
        self.assertEqual((self.spool / 'pending.json').stat().st_mode & 0o777, 0o600)

    def test_unsafe_spool_permissions_rejected(self):
        self.spool.mkdir()
        self.spool.chmod(0o755)
        self.append([sample()])
        with self.assertRaises(ValueError):
            mod.prepare(self.eve, self.spool)

    def test_no_observations_still_requires_ack_for_offset(self):
        invalid = sample()
        invalid['src_ip'] = '8.8.8.8'
        self.append([invalid])
        first = mod.prepare(self.eve, self.spool)
        self.assertEqual(first['observations'], 0)
        self.assertEqual(first['status'], 'prepared')
        self.assertEqual(mod.prepare(self.eve, self.spool)['status'], 'pending')
        mod.ack(self.spool, first['batch_id'])
        self.assertEqual(mod.prepare(self.eve, self.spool)['status'], 'idle')

    def test_replay_after_ack_checkpoint_before_unlink(self):
        self.append([sample()])
        first = mod.prepare(self.eve, self.spool)
        pending = mod.validated_pending(self.spool / 'pending.json')
        mod.safe_write(self.spool / 'checkpoint.json',
                       mod.canonical(pending['next_state']) + b'\n')
        # Simulate process crash between writing checkpoint and unlinking pending.
        self.assertEqual(mod.prepare(self.eve, self.spool)['status'], 'pending')
        mod.ack(self.spool, first['batch_id'])
        self.assertEqual(mod.prepare(self.eve, self.spool)['status'], 'idle')


if __name__ == '__main__':
    unittest.main()
