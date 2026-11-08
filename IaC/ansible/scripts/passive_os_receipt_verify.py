#!/usr/bin/env python3
"""OFFLINE verification of a sensor-side batch receipt against a router batch.

No SSH, automatic router acknowledgement, file mutation or Nmap.  This is an
integrity check, not authentication or proof that the remote host is trusted.
"""
import argparse
import json
import os
from pathlib import Path

from passive_os_batch_spool import canonical, validated_pending
from router_eve_minimizer import sha

MAX_RECEIPT_BYTES = 4096


def verify(pending_path, stored_path, receipt_path):
    pending = validated_pending(pending_path)
    if pending is None:
        raise ValueError('Missing prepared source batch')
    if stored_path.is_symlink() or receipt_path.is_symlink():
        raise ValueError('Refusing symlinked receipt artifacts')
    expected = canonical(pending) + b'\n'
    if stored_path.stat().st_size != len(expected):
        raise ValueError('Stored batch size does not match')
    if stored_path.read_bytes() != expected:
        raise ValueError('Stored batch content does not match')
    if receipt_path.stat().st_size > MAX_RECEIPT_BYTES:
        raise ValueError('Oversized receipt')
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    expected_receipt = {
        'protocol': 1,
        'batch_id': pending['batch_id'],
        'digest': pending['digest'],
        'stored_bytes': len(expected),
    }
    if receipt != expected_receipt:
        raise ValueError('Receipt does not match the prepared batch')
    return {
        'status': 'locally_verified',
        'batch_id': pending['batch_id'],
        'digest': pending['digest'],
        'stored_bytes': len(expected),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pending', type=Path, required=True)
    parser.add_argument('--stored', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.pending, args.stored, args.receipt),
                     sort_keys=True))


if __name__ == '__main__':
    main()
