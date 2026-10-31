#!/usr/bin/env python3
"""Offline-only durable intent journal for PPP QoS ownership.

Writes only inside an explicitly supplied test directory; no ip/tc/systemd.
Not a production state manager: recovery requires external kernel verification.
"""
import contextlib
import fcntl
import json
import os
from pathlib import Path
import tempfile

class JournalError(RuntimeError):
    pass

def validate_session(value):
    if value is None:
        return
    if not isinstance(value, dict) or set(value) != {"generation", "ifindex"}:
        raise JournalError("invalid session")
    if not isinstance(value["generation"], str) or not value["generation"] or len(value["generation"]) > 128:
        raise JournalError("invalid generation")
    if type(value["ifindex"]) is not int or value["ifindex"] <= 0:
        raise JournalError("invalid ifindex")

class Journal:
    def __init__(self, directory):
        self.dir = Path(directory)
        if not self.dir.is_dir() or self.dir.is_symlink():
            raise JournalError("test directory must already exist")
        self.path = self.dir / "ownership.json"
        self.lock_path = self.dir / "ownership.lock"

    @contextlib.contextmanager
    def locked(self):
        fd = os.open(self.lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    def read(self):
        if not self.path.exists():
            return {"version": 1, "phase": "clean", "owned": None, "target": None}
        if self.path.is_symlink():
            raise JournalError("refuse symlink")
        try:
            state = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise JournalError("corrupt state: recovery required") from exc
        if not isinstance(state, dict) or set(state) != {"version", "phase", "owned", "target"}:
            raise JournalError("invalid state")
        if type(state["version"]) is not int or state["version"] != 1 or state["phase"] not in ("clean", "pending"):
            raise JournalError("invalid state version/phase")
        validate_session(state["owned"])
        validate_session(state["target"])
        if state["phase"] == "clean" and state["target"] is not None:
            raise JournalError("clean state cannot have target")
        return state

    def write(self, state):
        if not isinstance(state, dict) or set(state) != {"version", "phase", "owned", "target"}:
            raise JournalError("invalid state")
        if type(state["version"]) is not int or state["version"] != 1 or state["phase"] not in ("clean", "pending"):
            raise JournalError("invalid state")
        validate_session(state["owned"])
        validate_session(state["target"])
        if state["phase"] == "clean" and state["target"] is not None:
            raise JournalError("invalid clean state")
        if self.path.is_symlink():
            raise JournalError("refuse symlink")
        payload = (json.dumps(state, sort_keys=True, separators=(",", ":")) + "\n").encode()
        fd, name = tempfile.mkstemp(prefix=".ownership-", dir=self.dir)
        try:
            with os.fdopen(fd, "wb") as out:
                os.fchmod(out.fileno(), 0o600)
                out.write(payload)
                out.flush()
                os.fsync(out.fileno())
            os.replace(name, self.path)
            dfd = os.open(self.dir, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def begin(self, owned, target):
        validate_session(owned)
        validate_session(target)
        with self.locked():
            state = self.read()
            if state["phase"] != "clean" or state["owned"] != owned:
                raise JournalError("ownership conflict / pending recovery")
            self.write({"version": 1, "phase": "pending", "owned": owned, "target": target})

    def finish(self, target, *, externally_verified=False):
        validate_session(target)
        if not externally_verified:
            raise JournalError("external verification required")
        with self.locked():
            state = self.read()
            if state["phase"] != "pending" or state["target"] != target:
                raise JournalError("no matching pending intent")
            self.write({"version": 1, "phase": "clean", "owned": target, "target": None})

    def recover_clean(self, *, externally_verified=False):
        if not externally_verified:
            raise JournalError("external verification required")
        with self.locked():
            state = self.read()
            if state["phase"] != "pending":
                raise JournalError("no pending recovery")
            self.write({"version": 1, "phase": "clean", "owned": None, "target": None})
