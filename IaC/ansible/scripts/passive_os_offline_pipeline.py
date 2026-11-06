#!/usr/bin/env python3
"""Stage 5.7E LOCAL synthetic end-to-end transport simulation, NOT deployable.

Runs only an explicitly opted-in Python -c local fixture. No SSH, keys,
network transport, source acknowledgments or checkpoint operations.
The receiver store is synthetic/local only and must be in a caller-owned
private test directory. Integration with production SSH is intentionally absent.
"""
import sys
from pathlib import Path

from passive_os_bounded_process import run_bounded_local_child
from passive_os_transport_plan import validate_retrieved_stdout
from passive_os_wire_receiver import receive_wire


def receive_local_fixture(argv, destination, *, synthetic_test_only=False,
                          timeout_seconds=2.0):
    """Run bounded synthetic producer, validate wire, then durable local receive.

    A failed producer, invalid wire or full store will not yield a success
    receipt. A retry of the same batch is deduplicated by the receiver.
    The API has no route to source-side ack().
    """
    if synthetic_test_only is not True:
        raise PermissionError("Only explicit synthetic local fixtures are accepted")
    if (not isinstance(argv, (list, tuple)) or len(argv) < 3 or
            argv[0] != sys.executable or argv[1] != "-c" or
            not all(isinstance(s, str) for s in argv)):
        raise PermissionError("Only Python -c local fixture processes allowed")
    if not isinstance(destination, Path):
        raise ValueError("Local test destination must be a Path")
    # Reject symlink at destination and all symlink ancestors; do not
    # create directories inside this function without separate review.
    if (not destination.is_dir() or destination.is_symlink() or
            destination.stat().st_mode & 0o077 or
            any(p.is_symlink() for p in destination.parents)):
        raise ValueError("Destination must be a private existing directory")
    stdout, stderr = run_bounded_local_child(
        argv, timeout_seconds=timeout_seconds)
    wire = validate_retrieved_stdout(stdout, 0, stderr)
    return receive_wire(stdout, destination)
