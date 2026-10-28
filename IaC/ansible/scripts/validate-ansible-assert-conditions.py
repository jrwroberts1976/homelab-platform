#!/usr/bin/env python3
"""Fail if an Ansible assert expression is accidentally parsed as a YAML mapping.

This catches YAML ':' followed by a space inside unquoted Jinja condition
expressions. 'ansible-playbook --syntax-check' alone does not detect the bug.
Only reads the supplied playbook(s); never contacts managed hosts.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import yaml


def walk(obj, trail):
    if isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from walk(value, f"{trail}[{i}]")
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if key in {"ansible.builtin.assert", "assert"} and isinstance(value, dict):
                that = value.get("that", [])
                if isinstance(that, str):
                    that = [that]
                if not isinstance(that, list):
                    yield f"{trail}.{key}.that: expected list/string, got {type(that).__name__}"
                else:
                    for i, expression in enumerate(that):
                        if not isinstance(expression, str):
                            yield (
                                f"{trail}.{key}.that[{i}]: expected expression string, "
                                f"got {type(expression).__name__}: {expression!r}"
                            )
            if key in {"when", "failed_when", "changed_when", "until"}:
                if isinstance(value, list):
                    for i, expression in enumerate(value):
                        if not isinstance(expression, str):
                            yield f"{trail}.{key}[{i}]: expected condition string, got {type(expression).__name__}"
                elif not isinstance(value, str):
                    yield f"{trail}.{key}: expected condition string, got {type(value).__name__}"
            yield from walk(value, f"{trail}.{key}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("playbooks", nargs="+", type=Path)
    args = parser.parse_args()
    problems = []
    for filename in args.playbooks:
        with filename.open(encoding="utf-8") as handle:
            document = yaml.safe_load(handle)
        if not isinstance(document, list):
            problems.append(f"{filename}: playbook root must be a list")
            continue
        problems += [f"{filename}: {message}" for message in walk(document, "$")]
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        raise SystemExit(1)
    print("PASS: Ansible assert and condition expressions are YAML strings in "
          + ", ".join(map(str, args.playbooks)))


if __name__ == "__main__":
    main()
