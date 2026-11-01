#!/usr/bin/env python3
"""Offline behavioural tests for router-qos-download-basic.sh.

All ip/tc/modprobe/flock/hostname calls are mocked. Runs against a disposable
copy of the checked-in controller, and never contacts router-01.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).with_name("router-qos-download-basic.sh")
MOCK = r'''#!/usr/bin/python3 -S
import json, os, pathlib, sys
path = pathlib.Path(os.environ["QOS_TEST_STATE"])
state = json.loads(path.read_text())
cmd = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
call = " ".join([cmd] + args)
state["calls"].append(call)
# A rejected kernel operation must not first mutate the mock kernel state.
# Earlier tests accidentally mutated then returned failure.
if state.get("fail") == call:
    path.write_text(json.dumps(state))
    sys.exit(1)
rc, out = 0, ""
if cmd == "hostname":
    out = "raspberrypi\n"
elif cmd in ("flock", "modprobe"):
    pass
elif cmd == "qos-stamp":
    if args == ["stamp"]:
        state["stamped"] = True
    elif args == ["verify-reattach"]:
        if not state.get("verified_owner", False):
            rc = 2
    elif args == ["release-after-delete"]:
        if state.get("ifbqosdl0", False):
            rc = 2
        else:
            state["stamped"] = False
            state["released"] = True
    else:
        rc = 2
elif cmd == "ip":
    if args[:3] == ["link", "show", "dev"]:
        rc = 0 if state.get(args[3], False) else 1
    elif args[:2] == ["link", "add"]:
        state["ifbqosdl0"] = True
    elif args[:2] == ["link", "del"]:
        state["ifbqosdl0"] = False
        state["cake_ifb"] = False
    elif args[:3] == ["link", "set", "ifbqosdl0"]:
        pass
    elif args[:2] == ["-br", "link"]:
        out = "ifbqosdl0 UP\n" if state.get("ifbqosdl0") else ""
    else:
        raise RuntimeError("unexpected ip args: " + repr(args))
elif cmd == "tc":
    if args[:2] == ["qdisc", "show"]:
        dev = args[-1]
        if dev == "eth1":
            out = "qdisc cake 8001: root bandwidth 13Mbit\n" if state["upload"] else "qdisc fq_codel 0: root\n"
        elif dev == "ppp0":
            out = "qdisc clsact ffff: parent ffff:fff1\n" if state["clsact"] else "qdisc noqueue 0: root\n"
        elif dev == "ifbqosdl0":
            out = "qdisc cake 8009: root bandwidth 43Mbit\n" if state["cake_ifb"] else "qdisc noqueue 0: root\n"
        else:
            raise RuntimeError("unexpected dev: " + dev)
    elif args[:3] == ["filter", "show", "dev"]:
        if state["filter"] == "owned":
            out = "filter protocol all pref 49132 matchall chain 0\n action order 1: mirred (Egress Redirect to device ifbqosdl0) stolen\n"
        elif state["filter"] == "foreign":
            out = "filter protocol all pref 99 matchall chain 0\n action order 1: mirred (Egress Redirect to device other0) stolen\n"
    elif args[:2] == ["qdisc", "add"]:
        if args[3] == "ifbqosdl0":
            state["cake_ifb"] = True
        elif args[3] == "ppp0":
            state["clsact"] = True
        else:
            raise RuntimeError("unexpected qdisc add: " + repr(args))
    elif args[:2] == ["filter", "add"]:
        state["filter"] = "owned"
    elif args[:2] == ["filter", "del"]:
        state["filter"] = "none"
    elif args[:2] == ["qdisc", "del"]:
        state["clsact"] = False
    else:
        raise RuntimeError("unexpected tc args: " + repr(args))
else:
    raise RuntimeError("unexpected executable: " + cmd)
path.write_text(json.dumps(state))
sys.stdout.write(out)
sys.exit(rc)
'''

class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.state = root / "state.json"
        mockdir = root / "bin"
        mockdir.mkdir()
        stub = mockdir / "mock"
        stub.write_text(MOCK)
        stub.chmod(0o755)
        for cmd in ("ip", "tc", "modprobe", "hostname", "flock", "qos-stamp"):
            (mockdir / cmd).symlink_to(stub)
        source = SOURCE.read_text()
        identity = '[[ "$(hostname -s)" == "raspberrypi" && $EUID -eq 0 ]] || exit 2'
        lock = 'exec 9>/run/lock/router-qos-download-basic.lock'
        self.assertIn(identity, source)
        self.assertIn(lock, source)
        source = source.replace(identity, '[[ "$(hostname -s)" == "raspberrypi" ]] || exit 2')
        source = source.replace(lock, f'exec 9>{root}/lock')
        source = source.replace('/usr/local/libexec/router-qos-download/stamp.py', str(stub))
        source = source.replace('/run/router-qos-download-basic.owner.json', str(root / 'owner.json'))
        source = source.replace('python3 "$STAMP_HELPER" stamp', 'qos-stamp stamp')
        source = source.replace('python3 "$STAMP_HELPER" release-after-delete',
                                'qos-stamp release-after-delete')
        source = source.replace('python3 "$STAMP_HELPER" verify-reattach',
                                'qos-stamp verify-reattach')
        self.script = root / "controller.sh"
        self.script.write_text(source)
        self.script.chmod(0o755)
        self.env = dict(os.environ, QOS_TEST_STATE=str(self.state), PATH=f'{mockdir}:{os.environ["PATH"]}')
        self.initial = {"ppp0": True, "ifbqosdl0": False, "upload": True,
                        "cake_ifb": False, "clsact": False, "filter": "none", "calls": []}
        self.save(dict(self.initial))

    def save(self, state):
        self.state.write_text(json.dumps(state))

    def load(self):
        return json.loads(self.state.read_text())

    def ensure(self):
        return subprocess.run(["bash", str(self.script), "ensure"],
                              text=True, capture_output=True, env=self.env, timeout=15)

    def test_initial_activation(self):
        result = self.ensure()
        state = self.load()
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual((state["cake_ifb"], state["clsact"], state["filter"]), (True, True, "owned"))

    def test_duplicate_up_is_non_destructive(self):
        self.assertEqual(self.ensure().returncode, 0)
        state = self.load()
        state["calls"] = []
        self.save(state)
        result = self.ensure()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any(" add " in call or " del " in call for call in self.load()["calls"]))

    def test_orphan_refused_without_deletion(self):
        self.save(dict(self.initial, ifbqosdl0=True, cake_ifb=True))
        self.assertNotEqual(self.ensure().returncode, 0)
        state = self.load()
        self.assertTrue(state["ifbqosdl0"])
        self.assertFalse(any("link del" in call for call in state["calls"]))

    def test_verified_orphan_reattaches_without_deletion(self):
        self.save(dict(self.initial, ifbqosdl0=True, cake_ifb=True, verified_owner=True))
        result = self.ensure()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        state = self.load()
        self.assertEqual(state["filter"], "owned")
        self.assertTrue(state["clsact"])
        self.assertTrue(state["ifbqosdl0"])
        self.assertFalse(any("link del" in c for c in state["calls"]))

    def test_unverified_orphan_remains_untouched(self):
        self.save(dict(self.initial, ifbqosdl0=True, cake_ifb=True))
        result = self.ensure()
        self.assertNotEqual(result.returncode, 0)
        state = self.load()
        self.assertFalse(state["clsact"])
        self.assertEqual(state["filter"], "none")
        self.assertFalse(any(" add " in c or " del " in c for c in state["calls"]))

    def test_reconnect_filter_failure_preserves_ifb_and_cleans_clsact(self):
        self.save(dict(self.initial, ifbqosdl0=True, cake_ifb=True,
                       verified_owner=True,
                       fail="tc filter add dev ppp0 ingress pref 49132 matchall action mirred egress redirect dev ifbqosdl0"))
        result = self.ensure()
        self.assertNotEqual(result.returncode, 0)
        state = self.load()
        self.assertTrue(state["ifbqosdl0"])
        self.assertFalse(state["clsact"])
        self.assertEqual(state["filter"], "none")
        self.assertFalse(any("link del" in c for c in state["calls"]))

    def test_foreign_filter_preserved(self):
        self.save(dict(self.initial, filter="foreign", clsact=True))
        self.assertNotEqual(self.ensure().returncode, 0)
        state = self.load()
        self.assertEqual(state["filter"], "foreign")
        self.assertFalse(any(" del " in call for call in state["calls"]))

    def test_filter_install_failure_rolls_back(self):
        self.save(dict(self.initial, fail="tc filter add dev ppp0 ingress pref 49132 matchall action mirred egress redirect dev ifbqosdl0"))
        self.assertNotEqual(self.ensure().returncode, 0)
        state = self.load()
        self.assertEqual((state["ifbqosdl0"], state["clsact"], state["filter"]), (False, False, "none"))

    def test_qdisc_install_failure_rolls_back(self):
        self.save(dict(self.initial, fail="tc qdisc add dev ppp0 clsact"))
        self.assertNotEqual(self.ensure().returncode, 0)
        self.assertFalse(self.load()["ifbqosdl0"])

    def test_missing_ppp_does_not_modify_network(self):
        self.save(dict(self.initial, ppp0=False))
        result = self.ensure()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any(" add " in c or " del " in c for c in self.load()["calls"]))

    def test_partial_ingress_state_refused(self):
        self.save(dict(self.initial, clsact=True, filter="none"))
        result = self.ensure()
        self.assertNotEqual(result.returncode, 0)
        state = self.load()
        self.assertTrue(state["clsact"])
        self.assertFalse(any(" add " in c or " del " in c for c in state["calls"]))

    def test_unmarked_cake_ifb_never_deleted(self):
        self.save(dict(self.initial, ifbqosdl0=True, cake_ifb=True))
        result = self.ensure()
        self.assertNotEqual(result.returncode, 0)
        state = self.load()
        self.assertTrue(state["ifbqosdl0"])
        self.assertFalse(any("link del" in c for c in state["calls"]))

    def test_manual_remove_refuses_unmarked_orphan(self):
        self.save(dict(self.initial, ifbqosdl0=True, cake_ifb=True))
        result = subprocess.run(["bash", str(self.script), "remove"],
                                text=True, capture_output=True, env=self.env, timeout=15)
        self.assertNotEqual(result.returncode, 0)
        state = self.load()
        self.assertTrue(state["ifbqosdl0"])
        self.assertFalse(any(" del " in c for c in state["calls"]))

    def test_manual_remove_refuses_foreign_ingress(self):
        self.save(dict(self.initial, ifbqosdl0=True, cake_ifb=True,
                       clsact=True, filter="foreign"))
        result = subprocess.run(["bash", str(self.script), "remove"],
                                text=True, capture_output=True, env=self.env, timeout=15)
        self.assertNotEqual(result.returncode, 0)
        state = self.load()
        self.assertTrue(state["ifbqosdl0"])
        self.assertEqual(state["filter"], "foreign")
        self.assertFalse(any(" del " in c for c in state["calls"]))

    def test_stamp_failure_rolls_back_new_ifb(self):
        self.save(dict(self.initial, fail="qos-stamp stamp"))
        result = self.ensure()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.load()["ifbqosdl0"])
        self.assertFalse(self.load().get("stamped", False))

    def test_failed_qdisc_install_releases_ownership_after_ifb_delete(self):
        self.save(dict(self.initial, fail="tc qdisc add dev ppp0 clsact"))
        self.assertNotEqual(self.ensure().returncode, 0)
        state = self.load()
        self.assertFalse(state["ifbqosdl0"])
        self.assertTrue(state.get("released", False))
        self.assertFalse(state.get("stamped", False))

    def test_existing_record_refuses_before_network_mutation(self):
        (Path(self.tmp.name) / "owner.json").write_text("old")
        result = self.ensure()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any(" add " in c or " del " in c for c in self.load()["calls"]))

    def test_successful_install_stamps(self):
        self.assertEqual(self.ensure().returncode, 0)
        self.assertTrue(self.load().get("stamped", False))

    def test_missing_upload_refuses(self):
        self.save(dict(self.initial, upload=False))
        self.assertNotEqual(self.ensure().returncode, 0)
        self.assertFalse(any(" add " in c or " del " in c for c in self.load()["calls"]))

if __name__ == "__main__":
    unittest.main(verbosity=2)
