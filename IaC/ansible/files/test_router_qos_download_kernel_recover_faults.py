#!/usr/bin/env python3
"""Failure injection for create-only legacy QoS recovery, using shell mocks.

Runs in a disposable directory, never issues real ip/tc/modprobe commands.
"""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).with_name("router-qos-download-kernel-recover-missing.sh")
STAGES = ["modprobe ifb", "ip link add", "ip link set",
          "tc qdisc add ifb", "tc qdisc add ppp", "tc filter add"]


class RecoveryInjectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.approval = self.root / "approval"
        self.approval.touch()
        self.calls = self.root / "calls"
        self.state = self.root / "state"
        source = SOURCE.read_text()
        swaps = {
            '[[ ${EUID} -eq 0 && "$(hostname -s)" == raspberrypi ]] || exit 2': 'true',
            'APPROVAL=/run/router-qos-download-kernel-recovery.approved':
                f'APPROVAL={self.approval}',
            'exec 9>/run/lock/router-qos-download-basic.lock':
                f'exec 9>{self.root / "lock"}',
            '/run/router-qos-download-basic.owner.json': str(self.root / "owner"),
        }
        for old, new in swaps.items():
            self.assertIn(old, source)
            source = source.replace(old, new)
        anchor = 'refuse() { echo "REFUSE: $*" >&2; exit 2; }'
        self.assertIn(anchor, source)
        mock = r"""
record() {
  printf '%s\n' "$1" >> "$CALLS"
  if [[ "${FAIL_AT:-}" == "$1" ]]; then return 17; fi
}
modprobe() { record "modprobe ifb"; }
ip() {
  if [[ "$*" == "link show dev ppp0" ]]; then return 0; fi
  if [[ "$*" == "link show dev ifbqosdl0" ]]; then
    [[ "${IFB_EXISTS:-0}" == 1 ]]; return; fi
  if [[ "$*" == "link add ifbqosdl0 type ifb" ]]; then record "ip link add"; return; fi
  if [[ "$*" == "link set ifbqosdl0 up" ]]; then record "ip link set"; return; fi
  return 99
}
tc() {
  case "$*" in
    "qdisc show dev eth1") echo "qdisc cake root bandwidth 13Mbit ptm overhead 30";;
    "filter show dev ppp0 ingress")
      if [[ -f "$CALLS" ]] && grep -qx "tc filter add" "$CALLS"; then
        echo "Redirect to device ifbqosdl0"
      fi;;
    "qdisc show dev ppp0")
      if [[ "${PPP_CLSACT:-0}" == 1 ]]; then echo "qdisc clsact"; fi;;
    "qdisc show dev ifbqosdl0") echo "qdisc cake root bandwidth 43Mbit";;
    "qdisc add dev ifbqosdl0 "*) record "tc qdisc add ifb";;
    "qdisc add dev ppp0 clsact") record "tc qdisc add ppp";;
    "filter add dev ppp0 "*) record "tc filter add";;
    *) return 99;;
  esac
}
flock() { :; }
"""
        source = source.replace(anchor, mock + "\n" + anchor)
        self.script = self.root / "script.sh"
        self.script.write_text(source)

    def run_actor(self, **extra):
        env = dict(os.environ, CALLS=str(self.calls), **extra)
        return subprocess.run(["bash", str(self.script), "restore-missing"],
                              env=env, text=True, capture_output=True, timeout=8)

    def recorded(self):
        return self.calls.read_text().splitlines() if self.calls.exists() else []

    def test_each_failed_kernel_command_stops_without_following_commands(self):
        for stage in STAGES:
            with self.subTest(stage=stage):
                self.calls.unlink(missing_ok=True)
                result = self.run_actor(FAIL_AT=stage)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                calls = self.recorded()
                self.assertEqual(calls, STAGES[:STAGES.index(stage) + 1])
                self.assertFalse(any(" del " in item or " replace " in item for item in calls))

    def test_existing_ifb_refuses_before_kernel_commands(self):
        result = self.run_actor(IFB_EXISTS="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.recorded(), [])

    def test_existing_owner_refuses_before_kernel_commands(self):
        (self.root / "owner").touch()
        result = self.run_actor()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.recorded(), [])

    def test_partial_existing_clsact_refuses_before_kernel_commands(self):
        result = self.run_actor(PPP_CLSACT="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.recorded(), [])

    def test_successful_mocked_create_only_path(self):
        result = self.run_actor()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.recorded(), STAGES)


if __name__ == "__main__":
    unittest.main(verbosity=2)
