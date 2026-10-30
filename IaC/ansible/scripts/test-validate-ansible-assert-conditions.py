#!/usr/bin/env python3
"""Regression checks: valid Ansible booleans must pass, YAML maps must fail.

Uses temporary *local* fixtures and never contacts the router.
Run from IaC/ansible:
  python3 scripts/test-validate-ansible-assert-conditions.py
"""
from pathlib import Path
import subprocess
import sys
import tempfile

VALIDATOR = Path(__file__).with_name("validate-ansible-assert-conditions.py")


def check_case(name: str, playbook: str, expect_success: bool, message: str = "") -> None:
    with tempfile.TemporaryDirectory(prefix="ansible-assert-regression-") as directory:
        file_path = Path(directory) / "case.yml"
        file_path.write_text(playbook, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(file_path)],
            capture_output=True,
            text=True,
            check=False,
        )
    if (result.returncode == 0) != expect_success:
        raise RuntimeError(
            f"{name}: expected success={expect_success}, got rc={result.returncode}: "
            f"{result.stdout} {result.stderr}"
        )
    if message and message not in result.stderr:
        raise RuntimeError(f"{name}: missing diagnostic {message!r}")
    print(f"PASS: {name}")


def main() -> None:
    check_case(
        "native boolean changed_when / failed_when / when / until",
        """---
- name: valid
  hosts: all
  tasks:
    - name: native false booleans
      ansible.builtin.command: /bin/true
      changed_when: false
      failed_when: false
      when: true
      until: true
    - name: boolean and expression lists
      ansible.builtin.command: /bin/true
      changed_when:
        - false
        - "'ok' == 'ok'"
      when:
        - true
        - "'ok' == 'ok'"
    - name: valid quoted assert expression containing colon
      ansible.builtin.assert:
        that:
          - "myvalue == 'END ANSIBLE MANAGED: router-metrics'"
""",
        True,
    )
    check_case(
        "malformed unquoted assert with YAML colon",
        """---
- name: invalid
  hosts: all
  tasks:
    - name: incorrect YAML mapping condition
      ansible.builtin.assert:
        that:
          - myvalue == 'END ANSIBLE MANAGED: router-metrics'
""",
        False,
        "expected expression string, got dict",
    )
    check_case(
        "malformed when condition with YAML colon",
        """---
- hosts: all
  tasks:
    - name: incorrect when condition
      ansible.builtin.command: /bin/true
      when:
        - expression == 'one: two'
""",
        False,
        "expected condition string/boolean, got dict",
    )
    print("ALL PASS: static validator regression cases")


if __name__ == "__main__":
    main()
