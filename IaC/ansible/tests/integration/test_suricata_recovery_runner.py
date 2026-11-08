#!/usr/bin/env python3
"""Run disposable localhost-only Suricata recovery scenarios."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAYBOOK = ROOT / "tests/integration/suricata-logrotate-recovery.yml"

SCENARIOS = {
    "success": (0, '"msg": "candidate policy"'),
    "failure": (0, '"msg": "original policy"'),
    "unexpected": (2, '"msg": "unexpected policy"'),
}


def main():
    for scenario, (expected_rc, expected_text) in SCENARIOS.items():
        result = subprocess.run(
            [
                "ansible-playbook",
                "-i", "localhost,",
                "-c", "local",
                str(PLAYBOOK),
                "-e", f"test_scenario={scenario}",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        output = result.stdout + result.stderr

        assert result.returncode == expected_rc, (
            f"{scenario}: unexpected exit code {result.returncode}\n"
            f"{output[-3000:]}"
        )

        assert expected_text in output, (
            f"{scenario}: expected final configuration missing"
        )

        assert "TASK [Remove disposable test directory]" in output
        assert "unreachable=0" in output

        if scenario == "unexpected":
            assert "REFUSE - unexpected configuration" in output
            assert "failed=1" in output
        else:
            assert "failed=0" in output

        print(f"{scenario.upper()}=PASS")

    print("LOCALHOST_RECOVERY_INTEGRATION=PASS")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError) as exc:
        print(f"INTEGRATION_TEST_FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
