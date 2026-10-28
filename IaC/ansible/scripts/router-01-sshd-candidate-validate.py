#!/usr/bin/env python3
"""C2b2: offline effective-policy check using an auto-deleted /run candidate.

Executed via Ansible's python3 - and stdin, as root on the physical Pi.
It does not write /etc/ssh, reload SSH, change keys, or enable forwarding.
Only a transient mode-0600 candidate under a mode-0700 /run directory
is written, then always removed.
"""

import glob
import hashlib
import json
import os
from pathlib import Path
import pwd
import stat
import subprocess
import sys
import tempfile

MAIN = Path("/etc/ssh/sshd_config")
EXPECTED_INCLUDE = "Include /etc/ssh/sshd_config.d/*.conf"
CANDIDATE = """
# BEGIN ANSIBLE MANAGED: router-metrics forwarding-only (C2b2)
Match User router-metrics
    PubkeyAuthentication yes
    AuthenticationMethods publickey
    PasswordAuthentication no
    KbdInteractiveAuthentication no
    PermitTTY no
    X11Forwarding no
    AllowAgentForwarding no
    AllowStreamLocalForwarding no
    AllowTcpForwarding local
    PermitOpen 127.0.0.1:9100
    PermitListen none
    GatewayPorts no
    PermitTunnel no
    PermitUserRC no
    MaxSessions 0
# END ANSIBLE MANAGED: router-metrics forwarding-only (C2b2)
"""

CONTEXTS = {
    "admin_direct": "user=james,host=admin-01,addr=192.168.2.48",
    "admin_via_asus": "user=james,host=admin-01,addr=192.168.2.1",
    "metrics_via_asus": "user=router-metrics,host=monitor-01,addr=192.168.2.1",
    "metrics_direct": "user=router-metrics,host=monitor-01,addr=192.168.2.52",
}
RESTRICTIONS = {
    "pubkeyauthentication": "yes",
    "authenticationmethods": "publickey",
    "passwordauthentication": "no",
    "kbdinteractiveauthentication": "no",
    "permittty": "no",
    "x11forwarding": "no",
    "allowagentforwarding": "no",
    "allowstreamlocalforwarding": "no",
    "allowtcpforwarding": "local",
    "permitopen": "127.0.0.1:9100",
    "permitlisten": "none",
    "gatewayports": "no",
    "permittunnel": "no",
    "permituserrc": "no",
    "maxsessions": "0",
    "forcecommand": "none",
}

def run_sshd(config, context=None, test=False):
    argv = ["/usr/sbin/sshd", "-t" if test else "-T", "-f", str(config)]
    if context is not None:
        argv.extend(["-C", context])
    res = subprocess.run(argv, capture_output=True, text=True, check=False)
    if res.returncode:
        # Expose only diagnostic syntax errors, never config contents or credentials.
        raise RuntimeError("sshd candidate validation failed: " + res.stderr.strip()[:450])
    return res.stdout

def parsed_policy(raw):
    policy = {}
    for line in raw.splitlines():
        name, _, value = line.partition(" ")
        policy[name] = value.strip()
    return policy

def main():
    if os.geteuid() != 0:
        raise RuntimeError("This audit requires root to evaluate sshd configuration safely")
    st = MAIN.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_uid != 0 or (st.st_mode & 0o022):
        raise RuntimeError("Unexpected SSH config ownership, type or writable permissions")
    user = pwd.getpwnam("router-metrics")
    if user.pw_dir != "/var/lib/router-metrics" or user.pw_shell != "/usr/sbin/nologin":
        raise RuntimeError("Monitoring service account changed")
    if list(glob.glob("/etc/ssh/sshd_config.d/*.conf")):
        raise RuntimeError("Unreviewed sshd config fragment detected")

    original = MAIN.read_bytes()
    main_hash = hashlib.sha256(original).hexdigest()
    if not original.endswith(b"\n"):
        raise RuntimeError("SSH config trailing newline changed")
    lines = original.decode("utf-8").splitlines()
    active = [(num, line.strip()) for num, line in enumerate(lines, 1)
              if line.strip() and not line.lstrip().startswith("#")]
    include = [(num, line) for num, line in active
               if line.split()[0].lower() == "include"]
    matches = [(num, line) for num, line in active
               if line.split()[0].lower() == "match"]
    if include != [(12, EXPECTED_INCLUDE)] or matches:
        raise RuntimeError("Main SSH configuration Include/Match order has drifted")

    # Evaluate the *currently installed* configuration as the baseline.
    run_sshd(MAIN, test=True)
    base_global = run_sshd(MAIN)
    base = {name: run_sshd(MAIN, context) for name, context in CONTEXTS.items()}

    # The only write is to a protected transient file beneath /run;
    # TemporaryDirectory cleans up even if validation fails.
    with tempfile.TemporaryDirectory(prefix="router-c2b2-sshd-", dir="/run") as directory:
        os.chmod(directory, 0o700)
        staged = Path(directory) / "sshd_config"
        staged.write_bytes(original + CANDIDATE.encode("utf-8"))
        staged.chmod(0o600)
        run_sshd(staged, test=True)
        proposed_global = run_sshd(staged)
        proposed = {name: run_sshd(staged, context) for name, context in CONTEXTS.items()}

    if base_global != proposed_global:
        raise RuntimeError("Candidate unexpectedly changes global effective SSH policy")
    for name in ("admin_direct", "admin_via_asus"):
        if proposed[name] != base[name]:
            raise RuntimeError("Candidate unexpectedly changes existing admin policy for " + name)
    details = {}
    for name in ("metrics_via_asus", "metrics_direct"):
        policy = parsed_policy(proposed[name])
        for directive, expected in RESTRICTIONS.items():
            observed = policy.get(directive, "<not-present>")
            if observed != expected:
                raise RuntimeError(
                    "Candidate monitoring policy mismatch for "
                    + name + ": " + directive + "=" + repr(observed)
                    + " expected " + repr(expected)
                )
        details[name] = {key: policy[key] for key in RESTRICTIONS}

    if MAIN.read_bytes() != original or hashlib.sha256(MAIN.read_bytes()).hexdigest() != main_hash:
        raise RuntimeError("Real sshd configuration changed unexpectedly during offline validation")
    print(json.dumps({
        "candidate_sshd_syntax_valid": True,
        "global_policy_unchanged": True,
        "admin_policy_unchanged_both_contexts": True,
        "monitoring_policy_restrictions_verified_both_contexts": True,
        "monitoring_effective_policy": details["metrics_via_asus"],
        "temporary_candidate_cleaned_up": True,
        "live_main_ssh_config_unchanged": True,
        "no_sshd_reload_or_network_changes": True,
    }, sort_keys=True))

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("C2b2 OFFLINE CANDIDATE CHECK FAILED: " + str(exc), file=sys.stderr)
        sys.exit(1)
