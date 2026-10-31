#!/usr/bin/env python3
"""Controller-only two-process advisory lock contention proof.

Does not access interfaces, tc, systemd or router. Uses isolated temporary files.
"""
import fcntl
import multiprocessing as mp
import os
import tempfile
import time
from pathlib import Path


def contender(lock_path, signal, result):
    with open(lock_path, "a+", encoding="utf-8") as handle:
        signal.put("attempt")
        start = time.monotonic()
        fcntl.flock(handle, fcntl.LOCK_EX)
        acquired = time.monotonic()
        result.put(acquired - start)
        fcntl.flock(handle, fcntl.LOCK_UN)


def main():
    context = mp.get_context("spawn")
    with tempfile.TemporaryDirectory(prefix="qos-lock-proof-") as directory:
        lock_path = str(Path(directory) / "reconcile.lock")
        signal = context.Queue()
        result = context.Queue()
        with open(lock_path, "a+", encoding="utf-8") as first:
            fcntl.flock(first, fcntl.LOCK_EX)
            second = context.Process(target=contender, args=(lock_path, signal, result))
            second.start()
            try:
                if signal.get(timeout=5) != "attempt":
                    raise RuntimeError("contender did not attempt lock")
                # Ensure the other process is waiting while the first still owns it.
                time.sleep(0.35)
                if not result.empty():
                    raise AssertionError("second process acquired the held lock")
            finally:
                fcntl.flock(first, fcntl.LOCK_UN)
            second.join(timeout=5)
            if second.is_alive():
                second.terminate()
                second.join()
                raise RuntimeError("contender did not complete")
            if second.exitcode != 0:
                raise RuntimeError(f"contender failed: {second.exitcode}")
        waited = result.get(timeout=2)
        if waited < 0.25:
            raise AssertionError(f"second process did not block: {waited:.3f}s")
        print(f"PASS: second process blocked on exclusive flock and resumed after release ({waited:.3f}s)")
        print("PASS: isolated files removed by temporary directory cleanup")


if __name__ == "__main__":
    main()
