#!/usr/bin/env python3
"""OFFLINE-ONLY sensor-side receiver for already-minimised batches.

No SSH, network, automatic router acknowledgement, or service installation.
Only run on synthetic inputs until the full production safety gates are met.
"""
import argparse
import fcntl
import json
import os
import re
from pathlib import Path

from passive_os_batch_spool import canonical, validated_pending
from router_eve_minimizer import safe_write

ID = re.compile(r'^[a-f0-9]{64}$')
MAX_RETAINED_BATCHES = 256
MAX_RETAINED_BYTES = 64 * 1024 * 1024
MAX_DIRECTORY_ENTRIES = 2 * MAX_RETAINED_BATCHES + 10


def capacity_check(destination, additional_bytes=0, new_batch=False):
    """Reject quota pressure and unsafe entries; never evict evidence.

    Caller must hold receiver lock when used in concurrent environments.
    """
    if destination.is_symlink() or destination.stat().st_mode & 0o077:
        raise ValueError('Unsafe receipt directory')
    total = 0
    batches = 0
    entries = 0
    for p in destination.iterdir():
        entries += 1
        if entries > MAX_DIRECTORY_ENTRIES:
            raise ValueError('Receiver directory entry limit exceeded')
        if p.name == '.lock':
            if p.is_symlink() or not p.is_file():
                raise ValueError('Unsafe receiver lock')
            continue
        if p.is_symlink() or not p.is_file():
            raise ValueError('Unsafe receiver directory entry')
        batch_name = p.name.endswith('.json') and ID.fullmatch(p.name[:-len('.json')])
        receipt_name = (p.name.endswith('.receipt.json') and
                        ID.fullmatch(p.name[:-len('.receipt.json')]))
        if not (batch_name or receipt_name):
            raise ValueError('Unexpected receiver file name')
        size = p.stat().st_size
        if size > MAX_RETAINED_BYTES:
            raise ValueError('Oversized receiver file')
        total += size
        if batch_name:
            batches += 1
    if batches + int(new_batch) > MAX_RETAINED_BATCHES:
        raise ValueError('Receiver batch quota exceeded')
    if total + additional_bytes > MAX_RETAINED_BYTES:
        raise ValueError('Receiver byte quota exceeded')
    return batches, total


def receive(batch_file, destination):
    """Store a validated batch, with a stable idempotent receipt.

    The receiving service will eventually hold an exclusive lock around this
    operation; this offline API intentionally does not open a network port.
    """
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
    record = {'protocol': 1, 'batch_id': batch_id,
              'digest': batch['digest'], 'stored_bytes': len(payload)}
    receipt_bytes = canonical(record) + b'\n'

    new_batch = not saved.exists()
    additional_bytes = (len(payload) if new_batch else 0)
    if not receipt.exists():
        additional_bytes += len(receipt_bytes)
    capacity_check(destination, additional_bytes, new_batch=new_batch)

    if saved.exists():
        if saved.is_symlink() or saved.read_bytes() != payload:
            raise ValueError('Existing batch differs; refuse overwrite')
    else:
        safe_write(saved, payload)

    if receipt.exists():
        if receipt.is_symlink() or json.loads(receipt.read_text()) != record:
            raise ValueError('Stored receipt differs; refuse overwrite')
        status = 'duplicate'
    else:
        safe_write(receipt, receipt_bytes)
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
