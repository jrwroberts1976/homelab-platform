#!/usr/bin/env python3
"""Synthetic LOCAL process tests; no SSH traffic, keys or router interaction."""
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from passive_os_bounded_process import run_bounded_local_child, MAX_SECONDS


def python_child(code):
    return [sys.executable, "-c", code]


class BoundedProcessTests(unittest.TestCase):
    def test_clean_output(self):
        stdout, stderr = run_bounded_local_child(
            python_child("import sys;sys.stdout.buffer.write(b'ok\\n')"))
        self.assertEqual(stdout, b"ok\n")
        self.assertEqual(stderr, b"")

    def test_both_streams_collected(self):
        out, err = run_bounded_local_child(
            python_child("import sys;sys.stdout.write('a');sys.stderr.write('b')"))
        self.assertEqual((out, err), (b"a", b"b"))

    def test_timeout_is_bounded(self):
        start = time.monotonic()
        with self.assertRaisesRegex(TimeoutError, "deadline"):
            run_bounded_local_child(
                python_child("import time;time.sleep(30)"), timeout_seconds=0.15)
        self.assertLess(time.monotonic() - start, 3)

    def test_stdout_overflow_rejected(self):
        with self.assertRaisesRegex(ValueError, "output limit"):
            run_bounded_local_child(
                python_child("import sys;sys.stdout.buffer.write(b'x'*64)"),
                stdout_limit=32)

    def test_stderr_overflow_rejected(self):
        with self.assertRaisesRegex(ValueError, "output limit"):
            run_bounded_local_child(
                python_child("import sys;sys.stderr.buffer.write(b'x'*64)"),
                stderr_limit=32)

    def test_nonzero_exit_refused_even_with_stdout(self):
        with self.assertRaisesRegex(ValueError, "nonzero"):
            run_bounded_local_child(
                python_child("import sys;sys.stdout.write('valid');sys.exit(7)"))

    def test_exact_output_ceiling_accepted(self):
        out, _ = run_bounded_local_child(
            python_child("import sys;sys.stdout.buffer.write(b'a'*32)"),
            stdout_limit=32)
        self.assertEqual(len(out), 32)

    def test_no_stdin_to_child(self):
        out, _ = run_bounded_local_child(
            python_child("import sys;sys.stdout.write(str(len(sys.stdin.read())))"))
        self.assertEqual(out, b"0")

    def test_unsafe_timeout_refused(self):
        for value in (0, -1, MAX_SECONDS + 1, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                run_bounded_local_child(python_child("pass"), timeout_seconds=value)

    def test_limits_cannot_exceed_ceiling(self):
        with self.assertRaises(ValueError):
            run_bounded_local_child(python_child("pass"), stdout_limit=2**25)
        with self.assertRaises(ValueError):
            run_bounded_local_child(python_child("pass"), stderr_limit=2**20)

    def test_no_shell_interpretation(self):
        out, _ = run_bounded_local_child(
            python_child("import sys;sys.stdout.write(sys.argv[1])") +
            ["hello;$(touch /tmp/SHOULD_NOT_EXIST)"])
        self.assertEqual(out, b"hello;$(touch /tmp/SHOULD_NOT_EXIST)")

    def test_invalid_argv_refused(self):
        for args in ([], ["echo", ""], ["echo", "bad\x00arg"], "echo hi"):
            with self.subTest(args=args), self.assertRaises(ValueError):
                run_bounded_local_child(args)

    def test_no_router_checkpoint_logic(self):
        import passive_os_bounded_process as m
        self.assertFalse(hasattr(m, "ack"))
        self.assertFalse(hasattr(m, "retrieval_argv"))


if __name__ == "__main__":
    unittest.main()
