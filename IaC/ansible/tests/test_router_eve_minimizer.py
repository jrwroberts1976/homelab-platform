#!/usr/bin/env python3
"""Offline-only extractor tests; never contact hosts or launch capture."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = (Path(__file__).resolve().parents[1] / 'scripts/router_eve_minimizer.py')
spec = importlib.util.spec_from_file_location('eve_minimizer', MODULE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def record(ip='192.168.2.113', kind='http', ua='Mozilla/5.0 (X11; CrOS x86_64 1)'):
    return {'timestamp': '2026-11-06T11:00:00+00:00', 'src_ip': ip,
            'event_type': kind, 'http': {'http_user_agent': ua},
            'url': '/secret-path', 'hostname': 'secret.example',
            'dns': {'rrname': 'secret.example'}, 'tls': {'sni': 'secret.example'}}


class OfflineMinimizerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'eve.json'

    def write(self, events):
        with self.path.open('ab') as out:
            for obj in events:
                out.write((json.dumps(obj) + '\n').encode())

    def test_minimizes_without_sensitive_fields(self):
        event = m.minimize(record())
        self.assertEqual(event['os_family_hint'], 'ChromeOS')
        self.assertEqual(set(event), {'timestamp','src_ip','event_type','os_family_hint'})
        self.assertNotIn('secret', json.dumps(event))

    def test_dns_tls_quic_are_only_metadata(self):
        for kind in ('dns', 'tls', 'quic'):
            self.assertEqual(set(m.minimize(record(kind=kind))),
                             {'timestamp', 'src_ip', 'event_type'})

    def test_rejects_inbound_or_non_client_ip(self):
        for ip in ('8.8.8.8', '192.168.2.1', '192.168.2.255', 'invalid'):
            self.assertIsNone(m.minimize(record(ip=ip)))

    def test_incremental_read_and_restart(self):
        self.write([record(), record(kind='dns')])
        first, state, meta = m.extract(self.path)
        self.assertEqual(len(first), 2)
        self.assertEqual(meta['read_lines'], 2)
        second, resumed, meta = m.extract(self.path, state)
        self.assertEqual(second, [])
        self.assertEqual(meta['read_lines'], 0)
        self.write([record(ua='Mozilla/5.0 (Windows NT 10.0)')])
        added, _, meta = m.extract(self.path, resumed)
        self.assertEqual(added[0]['os_family_hint'], 'Windows')
        self.assertEqual(meta['reset_reason'], 'continue')

    def test_copytruncate_resets_offset(self):
        self.write([record(), record(), record()])
        _, state, _ = m.extract(self.path)
        self.path.write_bytes((json.dumps(record(kind='tls')) + '\n').encode())
        events, _, meta = m.extract(self.path, state)
        self.assertEqual(meta['reset_reason'], 'truncated')
        self.assertEqual(len(events), 1)

    def test_inode_rotation_detected(self):
        self.write([record()])
        _, state, _ = m.extract(self.path)
        self.path.rename(self.path.with_suffix('.old'))
        self.path.write_bytes((json.dumps(record(kind='dns')) + '\n').encode())
        items, _, meta = m.extract(self.path, state)
        self.assertEqual(meta['reset_reason'], 'rotated')
        self.assertEqual(len(items), 1)

    def test_same_inode_rewrite_detected(self):
        self.write([record(ua='Android')])
        _, state, _ = m.extract(self.path)
        self.path.write_bytes((json.dumps(record(ua='Windows NT 10.0')) + '\n').encode())
        items, _, meta = m.extract(self.path, state)
        self.assertEqual(meta['reset_reason'], 'content_replaced')
        self.assertEqual(items[0]['os_family_hint'], 'Windows')

    def test_partial_line_waits_without_consuming(self):
        line = json.dumps(record()).encode()
        self.path.write_bytes(line)
        items, state, meta = m.extract(self.path)
        self.assertEqual((items, state['offset']), ([], 0))
        with self.path.open('ab') as f:
            f.write(b'\n')
        items, state, meta = m.extract(self.path, state)
        self.assertEqual(len(items), 1)

    def test_event_limit_bounds_read(self):
        self.write([record()] * 3)
        items, state, meta = m.extract(self.path, event_limit=1)
        self.assertEqual(len(items), 1)
        self.assertEqual(meta['read_lines'], 1)
        more, _, _ = m.extract(self.path, state, event_limit=1)
        self.assertEqual(len(more), 1)

    def test_timestamp_validation(self):
        a = record()
        a['timestamp'] = 'not-a-time'
        self.assertIsNone(m.minimize(a))

    def test_checkpoint_file_mode_private(self):
        target = Path(self.temp.name) / 'state.json'
        m.safe_write(target, b'{}')
        self.assertEqual(target.stat().st_mode & 0o777, 0o600)

    def test_invalid_state_rejected(self):
        target = Path(self.temp.name) / 'state.json'
        target.write_text('{"version":1,"dev":"bad","ino":1,"offset":0}')
        with self.assertRaises(ValueError):
            m.read_state(target)


if __name__ == '__main__':
    unittest.main()
