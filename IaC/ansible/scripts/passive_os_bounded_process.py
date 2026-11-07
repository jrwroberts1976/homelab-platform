#!/usr/bin/env python3
"""Stage 5.7D: LOCAL-TEST-ONLY bounded subprocess runner.

No executable entry point, no SSH call, no key material, no filesystem writes,
no checkpoint acknowledgment. Future transport integration requires approval.
Designed for Linux/POSIX local synthetic-child tests.
"""
import os
import selectors
import signal
import subprocess
import time

MAX_STDOUT_BYTES = 2 * 1024 * 1024 + 8192
MAX_STDERR_BYTES = 8192
MAX_SECONDS = 8.0
READ_CHUNK = 4096


def _kill_group(proc):
    """Terminate the full isolated child process group on any failure."""
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    finally:
        proc.wait()


def run_bounded_local_child(argv, timeout_seconds=MAX_SECONDS,
                            stdout_limit=MAX_STDOUT_BYTES,
                            stderr_limit=MAX_STDERR_BYTES):
    """Capture bounded output of one local test subprocess, including children.

    This lower-level primitive intentionally does not invoke retrieval_argv().
    No shells, stdin, inherited FDs or SSH environment are involved. A future
    production caller must add trust/key checks and explicit approval gates.
    """
    if (not isinstance(argv, (list, tuple)) or not argv or
            any(not isinstance(arg, str) or not arg or "\x00" in arg
                for arg in argv)):
        raise ValueError("Invalid subprocess argv")
    if (type(timeout_seconds) not in (int, float) or
            not 0 < timeout_seconds <= MAX_SECONDS):
        raise ValueError("Unsafe subprocess timeout")
    if (type(stdout_limit) is not int or not 0 < stdout_limit <= MAX_STDOUT_BYTES or
            type(stderr_limit) is not int or not 0 < stderr_limit <= MAX_STDERR_BYTES):
        raise ValueError("Unsafe output limits")

    proc = subprocess.Popen(
        argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, close_fds=True, start_new_session=True,
        shell=False,
    )
    selector = selectors.DefaultSelector()
    chunks = {proc.stdout: bytearray(), proc.stderr: bytearray()}
    ceilings = {proc.stdout: stdout_limit, proc.stderr: stderr_limit}
    deadline = time.monotonic() + timeout_seconds
    try:
        for fd in chunks:
            os.set_blocking(fd.fileno(), False)
            selector.register(fd, selectors.EVENT_READ)
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Subprocess exceeded deadline")
            for key, _ in selector.select(remaining):
                fd = key.fileobj
                # Read only the remaining allowance + one byte to detect overflow.
                count = min(READ_CHUNK, ceilings[fd] - len(chunks[fd]) + 1)
                block = os.read(fd.fileno(), count)
                if not block:
                    selector.unregister(fd)
                else:
                    chunks[fd].extend(block)
                    if len(chunks[fd]) > ceilings[fd]:
                        raise ValueError("Subprocess output limit exceeded")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Subprocess exceeded deadline")
        try:
            rc = proc.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            raise TimeoutError("Subprocess exceeded deadline") from None
        if rc != 0:
            raise ValueError("Subprocess failed with nonzero exit status")
        return bytes(chunks[proc.stdout]), bytes(chunks[proc.stderr])
    except BaseException:
        _kill_group(proc)
        raise
    finally:
        selector.close()
        proc.stdout.close()
        proc.stderr.close()
