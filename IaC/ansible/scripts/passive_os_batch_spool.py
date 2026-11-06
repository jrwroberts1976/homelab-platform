#!/usr/bin/env python3
"""OFFLINE-ONLY durable, single-outstanding-batch protocol for EVE minimiser.

No SSH, sockets, service installation, privilege changes or packet capture.
The 'ack' operation is a *simulation/manual test hook*, NOT proof of delivery.
Never schedule or point this script at live router-01 EVE.
"""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
import tempfile
from pathlib import Path

from router_eve_minimizer import extract, read_state, safe_write

MAX_BATCH_BYTES = 2 * 1024 * 1024
MAX_PENDING_BYTES = MAX_BATCH_BYTES + 8192
MAX_STATE_BYTES = 4096


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validated_pending(path):
    if not path.exists():
        return None
    if path.stat().st_size > MAX_PENDING_BYTES:
        raise ValueError('Pending batch exceeds cap')
    item = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(item, dict) or item.get('protocol') != 1:
        raise ValueError('Invalid pending batch')
    payload = item.get('observations')
    state = item.get('next_state')
    if not isinstance(payload, list) or not isinstance(state, dict):
        raise ValueError('Invalid pending batch fields')
    if len(canonical(payload)) > MAX_BATCH_BYTES:
        raise ValueError('Observation payload exceeds cap')
    if len(canonical(state)) > MAX_STATE_BYTES:
        raise ValueError('Next checkpoint exceeds cap')
    if item.get('digest') != digest(canonical(payload)):
        raise ValueError('Pending payload digest mismatch')
    expected = digest(canonical({'next_state': state,
                                 'digest': item['digest'],
                                 'previous_offset': item.get('previous_offset')}))
    if item.get('batch_id') != expected:
        raise ValueError('Pending batch identity mismatch')
    return item


def prepare(eve, spool):
    """Stage exactly one output batch; do not advance checkpoint until ack."""
    spool.mkdir(parents=True, exist_ok=True, mode=0o700)
    if spool.is_symlink() or spool.stat().st_mode & 0o077:
        raise ValueError('Spool directory must not be a symlink or group/world accessible')
    pending_path = spool / 'pending.json'
    checkpoint_path = spool / 'checkpoint.json'
    existing = validated_pending(pending_path)
    if existing:
        return {'status': 'pending', 'batch_id': existing['batch_id'],
                'observations': len(existing['observations'])}
    previous = read_state(checkpoint_path)
    observations, state, meta = extract(eve, previous)
    # Rotation/truncation after a checkpoint means continuity cannot be proven.
    # Do not publish a new batch or silently skip/replay a segment.
    # Operator-reviewed recovery policy is a separate future stage.
    if previous is not None and meta['reset_reason'] != 'continue':
        raise RuntimeError(
            "EVE continuity unverified: " + str(meta['reset_reason'])
            + "; checkpoint held, manual recovery required"
        )
    if meta['read_bytes'] == 0:
        return {'status': 'idle', 'observations': 0, 'reset_reason': meta['reset_reason']}
    payload_digest = digest(canonical(observations))
    offset = previous['offset'] if previous is not None else 0
    identity = digest(canonical({'next_state': state,
                                'digest': payload_digest,
                                'previous_offset': offset}))
    batch = {'protocol': 1, 'batch_id': identity,
             'digest': payload_digest, 'observations': observations,
             'previous_offset': offset, 'next_state': state}
    serialized = canonical(batch) + b'\n'
    if len(serialized) > MAX_PENDING_BYTES:
        raise ValueError('Pending batch exceeds limit; checkpoint unchanged')
    safe_write(pending_path, serialized)
    return {'status': 'prepared', 'batch_id': identity,
            'observations': len(observations), **meta}


def ack(spool, batch_id):
    """TEST HOOK ONLY: caller must independently prove downstream durability."""
    pending_path = spool / 'pending.json'
    checkpoint_path = spool / 'checkpoint.json'
    pending = validated_pending(pending_path)
    if not pending:
        raise ValueError('No pending batch to acknowledge')
    if batch_id != pending['batch_id']:
        raise ValueError('Wrong batch ID; no checkpoint advance')
    # Crash after checkpoint but before unlink is safe: may retransmit,
    # and downstream must deduplicate stable batch IDs.
    safe_write(checkpoint_path, canonical(pending['next_state']) + b'\n')
    pending_path.unlink()
    return {'status': 'acknowledged', 'batch_id': batch_id}


def run(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spool', required=True, type=Path)
    parser.add_argument('--eve', type=Path)
    parser.add_argument('--ack-id')
    args = parser.parse_args(argv)
    if (args.eve is None) == (args.ack_id is None):
        parser.error('Specify exactly one of --eve (prepare) or --ack-id (offline test)')
    # Do not create a new spool when acknowledging.
    if args.ack_id and not args.spool.is_dir():
        raise ValueError('Spool directory does not exist')
    args.spool.mkdir(parents=True, exist_ok=True, mode=0o700)
    if args.spool.is_symlink() or args.spool.stat().st_mode & 0o077:
        raise ValueError('Unsafe spool directory')
    lock_path = args.spool / '.lock'
    # Lock is in private spool; all writers must use this script.
    with lock_path.open('a+b') as lock:
        os.fchmod(lock.fileno(), 0o600)
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        if args.eve:
            output = prepare(args.eve, args.spool)
        else:
            output = ack(args.spool, args.ack_id)
    print(json.dumps(output, sort_keys=True))
    return output


if __name__ == '__main__':
    run()
