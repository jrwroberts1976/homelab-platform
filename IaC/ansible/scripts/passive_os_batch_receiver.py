#!/usr/bin/env python3
"""Offline-only sensor-side receiver for already-minimised batches.

No SSH/network, automatic acknowledgment, OS classification, or service units.
Receipt indicates the local file was written, NOT delivery back to router-01.
"""
import argparse
import fcntl
import json
import os
import re
from pathlib import Path

from passive_os_batch_spool import canonical, digest, validated_pending
from router_eve_minimizer import safe_write

ID = re.compile(r'^[a-f0-9]{64}$')


def receive(batch_file, destination):
    batch = validated_pending(batch_file)
    if batch is None:
        raise ValueError('No input batch')
    batch_id = batch['batch_id']
    if not ID.fullmatch(batch_id):
        raise ValueError('Invalid batch ID')
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    if destination.is_symlink() or destination.stat().st_mode & 0o077:
        raise ValueError('Unsafe receipt directory')
    saved = destination / (batch_id + '.json')
    receipt = destination / (batch_id + '.receipt.json')
    payload = canonical(batch) + b'\n'
    if saved.exists():
        if saved.stat().st_size > len(payload) or saved.read_bytes() != payload:
            raise ValueError('Existing batch differs; refuse overwrite')
    else:
        safe_write(saved, payload)
    # At-least-once, content-addressed receipt. No duplicate file created.
    record = {'protocol': 1, 'batch_id': batch_id,
              'digest': batch['digest'], 'stored_bytes': len(payload)}
    if receipt.exists():
        if json.loads(receipt.read_text()) != record:
            raise ValueError('Stored receipt differs; refuse overwrite')
        status = 'duplicate'
    else:
        safe_write(receipt, canonical(record) + b'\n')
        status = 'stored'
    return {'status': status, **record}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    if args.destination.is_symlink() or args.destination.stat().st_mode & 0o077:
        raise ValueError('Unsafe receipt directory')
    with (args.destination / '.lock').open('a+b') as lock:
        os.fchmod(lock.fileno(), 0o600)
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        result = receive(args.batch, args.destination)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
