"""Prevent overlapping Nmap worker instances."""

import fcntl
import os
from contextlib import contextmanager
from pathlib import Path


class WorkerBusy(Exception):
    """Another worker already holds the lock."""


@contextmanager
def exclusive_worker_lock(path):
    """Hold an exclusive lock for the entire worker execution."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        os.fchmod(fd, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise WorkerBusy("Another Nmap worker is running") from exc

        yield
    finally:
        os.close(fd)
