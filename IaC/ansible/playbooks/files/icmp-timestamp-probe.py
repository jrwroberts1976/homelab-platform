#!/usr/bin/env python3
"""Bounded, non-mutating ICMPv4 timestamp test using the Python stdlib.

Execute on greenbone-01 as root via Ansible command/python -c.
Only the target IP, packet counts and verdict are emitted (no timestamps).
"""
import ipaddress
import os
import select
import socket
import struct
import sys
import time

TYPE_REQUEST = 13
TYPE_REPLY = 14
TIMEOUT_SECONDS = 1.5
ATTEMPTS = 3


def checksum(data):
    if len(data) % 2:
        data += b"\x00"
    words = struct.unpack("!" + "H" * (len(data) // 2), data)
    total = sum(words)
    while total >> 16:
        total = (total & 0xffff) + (total >> 16)
    return ~total & 0xffff


def make_packet(icmp_type, identifier, sequence, originate, receive=0, transmit=0):
    message = struct.pack(
        "!BBHHHIII", icmp_type, 0, 0, identifier, sequence,
        originate, receive, transmit,
    )
    signed_checksum = checksum(message)
    return struct.pack(
        "!BBHHHIII", icmp_type, 0, signed_checksum,
        identifier, sequence, originate, receive, transmit,
    )


def is_matching_reply(datagram, sender, target, identifier, sequence):
    if sender != target or len(datagram) < 40:
        return False
    version = datagram[0] >> 4
    ihl = (datagram[0] & 15) * 4
    if version != 4 or ihl < 20 or len(datagram) < ihl + 20:
        return False
    if datagram[9] != socket.IPPROTO_ICMP:
        return False
    if socket.inet_ntoa(datagram[12:16]) != target:
        return False
    icmp = datagram[ihl:]
    if checksum(icmp) != 0:
        return False
    kind, code, _, recv_identifier, recv_sequence = struct.unpack(
        "!BBHHH", icmp[:8]
    )
    return (kind == TYPE_REPLY and code == 0
            and recv_identifier == identifier and recv_sequence == sequence)


def self_test():
    identifier, sequence, origin = 345, 2, 123456
    request = make_packet(TYPE_REQUEST, identifier, sequence, origin)
    reply = make_packet(TYPE_REPLY, identifier, sequence, origin, origin + 2, origin + 4)
    assert len(request) == 20 and len(reply) == 20
    assert checksum(request) == 0 and checksum(reply) == 0
    ip = bytearray(20)
    ip[0] = 0x45
    ip[9] = socket.IPPROTO_ICMP
    ip[12:16] = socket.inet_aton("192.168.2.195")
    datagram = bytes(ip) + reply
    assert is_matching_reply(
        datagram, "192.168.2.195", "192.168.2.195", identifier, sequence
    )
    assert not is_matching_reply(
        datagram, "192.168.2.123", "192.168.2.195", identifier, sequence
    )
    assert not is_matching_reply(
        datagram, "192.168.2.195", "192.168.2.195", identifier, sequence + 1
    )
    assert not is_matching_reply(
        bytes(ip) + request, "192.168.2.195", "192.168.2.195", identifier, sequence
    )
    print("ICMP_TIMESTAMP_PROBE_SELF_TEST=PASS")


def main(target):
    target = str(ipaddress.IPv4Address(target))
    identifier = os.getpid() & 0xffff
    replies = 0
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
            sock.setblocking(False)
            for sequence in range(1, ATTEMPTS + 1):
                milliseconds_utc = (time.time_ns() // 1_000_000) % 86_400_000
                request = make_packet(TYPE_REQUEST, identifier, sequence, milliseconds_utc)
                sock.sendto(request, (target, 0))
                deadline = time.monotonic() + TIMEOUT_SECONDS
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    readable, _, _ = select.select([sock], [], [], remaining)
                    if not readable:
                        break
                    datagram, (sender, _) = sock.recvfrom(4096)
                    if is_matching_reply(datagram, sender, target, identifier, sequence):
                        replies += 1
                        break
    except (OSError, ValueError) as exc:
        print("ICMP_TIMESTAMP_PROBE_ERROR=" + type(exc).__name__, file=sys.stderr)
        return 2

    print("ICMP_TIMESTAMP_TARGET=" + target)
    print("ICMP_TIMESTAMP_REQUESTS_SENT=" + str(ATTEMPTS))
    print("ICMP_TIMESTAMP_REPLIES_MATCHED=" + str(replies))
    print("ICMP_TIMESTAMP_RESULT=" +
          ("REPLY_CONFIRMED" if replies else "NO_REPLY_OBSERVED"))
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
    elif len(sys.argv) == 2:
        sys.exit(main(sys.argv[1]))
    else:
        print("Usage: probe.py <IPv4-address> | --self-test", file=sys.stderr)
        sys.exit(2)
