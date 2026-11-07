#!/usr/bin/env python3
"""Offline-only, bounded Suricata EVE -> minimal OS observations.

No network access, no service management, no Nmap. This prototype must NOT be
pointed at live router EVE before an explicit production approval and review.
"""
import argparse
import hashlib
import ipaddress
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

LAN = ipaddress.ip_network('192.168.2.0/24')
MAX_BYTES = 1024 * 1024
MAX_EVENTS = 2000
MAX_LINE = 8192
MAX_STATE = 4096
TAIL_WINDOW = 64


def os_family_from_ua(value):
    if not isinstance(value, str):
        return None
    ua = value[:1024].lower()
    if 'cros ' in ua or 'chromebook' in ua:
        return 'ChromeOS'
    if 'android' in ua:
        return 'Android'
    if any(x in ua for x in ('iphone', 'ipad', 'ipod')):
        return 'iOS/iPadOS'
    if 'windows nt' in ua:
        return 'Windows'
    if 'mac os x' in ua or 'macintosh' in ua:
        return 'macOS'
    if 'linux' in ua or 'x11;' in ua:
        return 'Linux'
    return None


def timestamp_seconds(value):
    if not isinstance(value, str) or len(value) > 64:
        return None
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            return None
        stamp = int(dt.astimezone(timezone.utc).timestamp())
        return stamp if 1577836800 <= stamp <= 4102444800 else None
    except (ValueError, OverflowError, OSError):
        return None


def minimize(event):
    if not isinstance(event, dict):
        return None
    kind = event.get('event_type')
    if kind not in ('dns', 'http', 'tls', 'quic'):
        return None
    ip = event.get('src_ip')
    try:
        addr = ipaddress.ip_address(ip)
    except (ValueError, TypeError):
        return None
    if (addr not in LAN or addr in
            (LAN.network_address, LAN.broadcast_address, LAN.network_address + 1)):
        return None
    stamp = timestamp_seconds(event.get('timestamp'))
    if stamp is None:
        return None
    result = {'timestamp': stamp, 'src_ip': str(addr), 'event_type': kind}
    if kind == 'http':
        family = os_family_from_ua((event.get('http') or {}).get('http_user_agent')
                                   if isinstance(event.get('http'), dict) else None)
        if family:
            result['os_family_hint'] = family
    return result


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_write(path, data):
    # Strict local files only, atomic replacement and no transient plaintext exposure.
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temp = tempfile.mkstemp(prefix='.' + path.name + '.', dir=str(path.parent))
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def read_state(path):
    if not path.exists():
        return None
    if path.stat().st_size > MAX_STATE:
        raise ValueError('Checkpoint exceeds size limit')
    state = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(state, dict) or state.get('version') != 1:
        raise ValueError('Invalid checkpoint')
    if any(not isinstance(state.get(k), int) or state[k] < 0
           for k in ('dev', 'ino', 'offset')):
        raise ValueError('Invalid checkpoint position')
    return state


def extract(path, state=None, byte_limit=MAX_BYTES, event_limit=MAX_EVENTS):
    """Read a bounded complete-line chunk; never scan the whole EVE file.

    Returns (minimized, next_state, metadata). Caller writes output atomically
    before checkpoint; on crash an output batch may replay, so consumers must
    deduplicate by batch/observation identity in a later live pipeline.
    """
    if not 1 <= byte_limit <= MAX_BYTES or not 1 <= event_limit <= MAX_EVENTS:
        raise ValueError('Limits exceed safety ceiling')
    with path.open('rb') as source:
        stat = os.fstat(source.fileno())
        offset = 0
        reason = 'initial'
        if state is not None:
            if state['dev'] == stat.st_dev and state['ino'] == stat.st_ino:
                offset = state['offset']
                if offset > stat.st_size:
                    offset, reason = 0, 'truncated'
                else:
                    window = min(offset, TAIL_WINDOW)
                    source.seek(offset - window)
                    previous = source.read(window)
                    if sha(previous) != state.get('tail_sha'):
                        offset, reason = 0, 'content_replaced'
                    else:
                        reason = 'continue'
            else:
                reason = 'rotated'
        source.seek(offset)
        items = []
        consumed = 0
        lines = 0
        while lines < event_limit and consumed < byte_limit:
            room = min(MAX_LINE + 1, byte_limit - consumed)
            if room < MAX_LINE + 1:
                break  # Never consume a line with insufficient remaining budget.
            raw = source.readline(MAX_LINE + 1)
            if not raw:
                break
            if len(raw) > MAX_LINE or not raw.endswith(b'\n'):
                break  # Leave oversized/partial line untouched; fail closed.
            consumed += len(raw)
            lines += 1
            try:
                observation = minimize(json.loads(raw))
            except (UnicodeError, ValueError, TypeError):
                observation = None
            if observation is not None:
                items.append(observation)
        next_offset = offset + consumed
        source.seek(max(0, next_offset - TAIL_WINDOW))
        tail = source.read(min(next_offset, TAIL_WINDOW))
        next_state = {'version': 1, 'dev': stat.st_dev, 'ino': stat.st_ino,
                      'offset': next_offset, 'tail_sha': sha(tail)}
        return items, next_state, {'read_bytes': consumed, 'read_lines': lines,
                                   'reset_reason': reason}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--eve', type=Path, required=True)
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.eve.resolve() in (args.output.resolve(), args.checkpoint.resolve()):
        raise ValueError('Input file cannot be overwritten')
    events, next_state, meta = extract(args.eve, read_state(args.checkpoint))
    # Output before updating the checkpoint: at-least-once on crash, not exactly once.
    payload = b''.join((json.dumps(x, sort_keys=True) + '\n').encode('utf-8') for x in events)
    safe_write(args.output, payload)
    safe_write(args.checkpoint, (json.dumps(next_state, sort_keys=True) + '\n').encode('utf-8'))
    print(json.dumps({'observations': len(events), **meta}, sort_keys=True))


if __name__ == '__main__':
    main()
