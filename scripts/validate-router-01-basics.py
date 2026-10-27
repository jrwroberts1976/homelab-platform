#!/usr/bin/env python3
"""Offline router-01 config/safety contract validator (no host contact)."""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = pathlib.Path(__file__).resolve().parents[1]
ANSIBLE = ROOT / "IaC" / "ansible"
TEMPLATES = ANSIBLE / "roles" / "router_basics" / "templates"


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def maybe_check_syntax(executable: str, arguments: list[str]) -> None:
    import shutil

    if shutil.which(executable):
        command = [executable, *arguments]
        # nft -c may still require CAP_NET_ADMIN to query rule metadata.
        if executable == "nft" and os.environ.get("GITHUB_ACTIONS") == "true":
            command = ["sudo", "-n", *command]
        subprocess.run(command, check=True, timeout=20)
        print("PASS: " + " ".join(command))
    else:
        print("SKIP: " + executable + " not installed for native syntax check")


def main() -> None:
    inventory = yaml.safe_load(
        (ANSIBLE / "inventory" / "router-01-staging.yml").read_text()
    )
    hosts = inventory["all"]["children"]["router_staging"]["hosts"]
    check(list(hosts) == ["router-01"], "Staging inventory must target only router-01")
    conf = hosts["router-01"]
    check(conf["ansible_host"] == "192.168.3.1", "Wrong router staging IP")
    check(conf["router_expected_wan_mac"] == "00:24:9b:63:b3:8a", "Unknown WAN NIC")
    check(conf["router_expected_lan_mac"] == "d8:3a:dd:5a:51:44", "Unknown LAN NIC")
    check(conf["router_lan_interface"] == "eth0", "LAN must be eth0")
    check(conf["router_wan_interface"] == "eth1", "WAN must be eth1")
    check(conf["router_dhcp_start"] == "192.168.3.100", "Unexpected DHCP start")
    check(conf["router_dhcp_end"] == "192.168.3.199", "Unexpected DHCP end")
    # The old SSH management address remains in the future-only pre-stage
    # inventory until every prospective config is safely rendered.
    prestage_inv = yaml.safe_load(
        (ANSIBLE / "inventory" / "router-01-prestage.yml").read_text()
    )
    prestage_hosts = prestage_inv["all"]["children"]["router_prestage"]["hosts"]
    check(list(prestage_hosts) == ["router-01"], "Pre-stage may only target router-01")
    check(prestage_hosts["router-01"]["ansible_host"] == "192.168.2.220",
          "Pre-stage must keep original SSH address")
    check(prestage_hosts["router-01"]["router_lan_address"] == "192.168.3.1",
          "Final LAN target changed unexpectedly")

    prestage_play = yaml.safe_load(
        (ANSIBLE / "playbooks" / "router-01-prestage.yml").read_text()
    )[0]
    check(prestage_play["hosts"] == "router_prestage", "Wrong pre-stage play target")
    check(prestage_play["gather_facts"] is False,
          "Must refuse locally before any SSH contact")
    check(prestage_play["vars"]["router_prestage_approved"] is False,
          "Pre-stage approval must default OFF")
    pre_tasks = prestage_play["pre_tasks"]
    check(pre_tasks[0].get("delegate_to") == "localhost",
          "First pre-stage guard must run locally")
    check("router_prestage_approved | bool" in
          pre_tasks[0]["ansible.builtin.assert"]["that"],
          "Pre-stage local approval guard missing")
    prestage_src = (ANSIBLE / "playbooks" / "router-01-prestage.yml").read_text()
    check("router_conversion_marker.stat.isreg" in prestage_src,
          "Must require new-image attestation file")
    check("router_current_management_ip in ansible_facts.all_ipv4_addresses"
          in prestage_src, "Must guard old management address")
    for forbidden in ("ansible.builtin.apt:", "ansible.builtin.systemd_service:",
                      "networkctl reconfigure", "/etc/systemd/network/10-router-lan.network"):
        check(forbidden not in prestage_src,
              f"Pre-stage must not activate/modify live networking: {forbidden}")

    pppoe_play = yaml.safe_load(
        (ANSIBLE / "playbooks" / "router-01-pppoe-prestage.yml").read_text()
    )[0]
    check(pppoe_play["hosts"] == "router_prestage", "PPPoE stage wrong inventory")
    check(pppoe_play["gather_facts"] is False, "PPPoE stage must guard before SSH")
    check(pppoe_play["vars"]["router_pppoe_prestage_approved"] is False,
          "PPPoE stage must default to refused")
    check(pppoe_play["pre_tasks"][0].get("delegate_to") == "localhost",
          "PPPoE stage must refuse from controller before contacting host")
    pppoe_src = (ANSIBLE / "playbooks" / "router-01-pppoe-prestage.yml").read_text()
    for required in ("router_pppoe_conversion_marker.stat.isreg",
                     "router_current_management_ip in ansible_facts.all_ipv4_addresses",
                     "router_expected_wan_mac",
                     "router_expected_lan_mac",
                     "no_log: true",
                     "router_stage_directory }}/pppoe",
                     "router_pppoe_service_status.stdout | trim != 'active'"):
        check(required in pppoe_src, "PPPoE prestage guard missing: " + required)
    for forbidden in ("ansible.builtin.apt:",
                      "ansible.builtin.systemd_service:",
                      "/etc/ppp/peers/homelab-wan",
                      "/etc/systemd/network/20-router-wan.network",
                      "networkctl reconfigure"):
        check(forbidden not in pppoe_src,
              "PPPoE prestage must not touch active paths: " + forbidden)

    audit = yaml.safe_load(
        (ANSIBLE / "playbooks" / "router-01-docker-retirement-readonly.yml").read_text()
    )[0]
    check(audit["hosts"] == "docker-01", "Read-only audit must target active docker-01")
    for task in audit["tasks"]:
        modules = [key for key in task if key.startswith("ansible.builtin.")]
        check(all(key in {"ansible.builtin.assert", "ansible.builtin.command",
                          "ansible.builtin.shell", "ansible.builtin.debug"}
                  for key in modules),
              "Docker retirement audit has a mutating Ansible module")

    dependency_audit = yaml.safe_load(
        (ANSIBLE / "playbooks" / "router-01-inplace-dependencies-readonly.yml").read_text()
    )[0]
    check(dependency_audit["hosts"] == "docker-01",
          "In-place dependency audit must target only docker-01")
    dependency_src = (
        ANSIBLE / "playbooks" / "router-01-inplace-dependencies-readonly.yml"
    ).read_text()
    check("apt-get" in dependency_src and "- -s" in dependency_src,
          "Docker package removal impact must be simulation-only")
    check("nmcli -g" in dependency_src,
          "Need non-secret NetworkManager profile inventory")
    for task in dependency_audit["tasks"]:
        modules = [key for key in task if key.startswith("ansible.builtin.")]
        check(all(key in {"ansible.builtin.assert", "ansible.builtin.command",
                          "ansible.builtin.shell", "ansible.builtin.debug"}
                  for key in modules),
              "In-place dependency audit contains mutating Ansible modules")
    check(not any("--show-secrets" in line and not line.lstrip().startswith("#")
                  for line in dependency_src.splitlines()),
          "Do not expose NetworkManager profile secrets")

    retired = yaml.safe_load(
        (ANSIBLE / "playbooks" / "router-01-docker-retirement-approved.yml").read_text()
    )[0]
    check(retired["hosts"] == "docker-01",
          "Docker retirement must target current managed docker-01")
    check(retired["gather_facts"] is False,
          "Docker retirement must check approvals before SSH")
    approvals = [
        "router_docker_retirement_approved",
        "router_komodo_deregistration_verified",
        "router_trivy_monitoring_reconciled",
        "router_retirement_backup_verified",
        "router_retirement_console_ready",
    ]
    for key in approvals:
        check(retired["vars"][key] is False,
              f"Docker retirement approval {key} must default false")
        check(f"{key} | bool" in
              retired["pre_tasks"][0]["ansible.builtin.assert"]["that"],
              f"Controller must verify {key}")
    check(retired["pre_tasks"][0]["delegate_to"] == "localhost",
          "Docker retirement must refuse locally before SSH")
    retired_source = (
        ANSIBLE / "playbooks" / "router-01-docker-retirement-approved.yml"
    ).read_text()
    check("apt-get, -s, remove" in retired_source,
          "Docker retirement requires apt simulation before uninstall")
    check("/var/lib/prometheus/node-exporter/homelab_container_estate.prom" in retired_source,
          "Retire Docker-only scan metric to avoid stale successful scans")
    check("homelab-trivy-docker.service" in retired_source,
          "Stop in-flight Docker-specific scan before runtime removal")
    check("autoremove: false" in retired_source
          and "purge: false" in retired_source,
          "Docker retirement may not purge or autoremove")
    check("docker, compose, -f" in retired_source
          and " down]" in retired_source,
          "Docker retirement must stop ONLY exact Compose projects")
    for forbidden in (
        "docker system prune", "--volumes", "rm -rf /var/lib/docker",
        "netplan apply", "nmcli connection modify", "hostnamectl set-hostname",
    ):
        # The playbook comments may mention avoided behaviours;
        # disallow only the actual commands/modules at runtime.
        commands = [
            str(task.get("ansible.builtin.command", ""))
            for task in retired.get("tasks", [])
        ]
        check(not any(forbidden in cmd for cmd in commands),
              f"Unsafe command in Docker retirement: {forbidden}")

    last_audit = yaml.safe_load(
        (ANSIBLE / "playbooks" / "router-01-retirement-config-readonly.yml").read_text()
    )[0]
    check(last_audit["hosts"] == "docker-01",
          "Last pre-retirement audit must only target current docker-01")
    for task in last_audit["tasks"]:
        modules = [key for key in task if key.startswith("ansible.builtin.")]
        check(all(key in {"ansible.builtin.assert", "ansible.builtin.command",
                          "ansible.builtin.shell", "ansible.builtin.stat",
                          "ansible.builtin.debug"} for key in modules),
              "Last pre-retirement audit contains mutating Ansible modules")
    last_src = (ANSIBLE / "playbooks" / "router-01-retirement-config-readonly.yml").read_text()
    check("NETPLAN=" in last_src and "NGINX_SITES=" in last_src,
          "Last audit must report safe Netplan/Nginx evidence")
    check("DOCKER_TRIVY_TEXTFILE_PRESENT=" in last_src,
          "Docker metrics retirement requires textfile presence evidence")

    # Package installation may occur only after approved conversion and while
    # the old SSH IP is still present. dpkg start attempts must be suppressed.
    package_play = yaml.safe_load(
        (ANSIBLE / "playbooks" / "router-01-package-stage.yml").read_text()
    )[0]
    check(package_play["hosts"] == "router_prestage", "Package stage wrong hosts")
    check(package_play["gather_facts"] is False, "Package guard must precede SSH")
    check(package_play["vars"]["router_package_stage_approved"] is False,
          "Package stage must default OFF")
    check(package_play["pre_tasks"][0].get("delegate_to") == "localhost",
          "Package first guard must run locally")
    package_src = (ANSIBLE / "playbooks" / "router-01-package-stage.yml").read_text()
    check("policy_rc_d: 101" in package_src, "Missing maintainer start suppression")
    check("masked: true" in package_src, "Unstarted services must be masked")
    check("router_conversion_attestation.stat.isreg" in package_src,
          "Package stage must check image marker")
    check("router_current_management_ip in ansible_facts.all_ipv4_addresses"
          in package_src, "Package stage must retain old IP")
    check("/etc/systemd/network/" not in package_src,
          "Package stage must not write live networkd configuration")

    recovery_play = yaml.safe_load(
        (ANSIBLE / "playbooks" / "router-01-rollback-prepare.yml").read_text()
    )[0]
    check(recovery_play["hosts"] == "router_prestage",
          "Recovery helper wrong hosts")
    check(recovery_play["gather_facts"] is False,
          "Recovery helper must gate before SSH")
    check(recovery_play["vars"]["router_rollback_prepare_approved"] is False,
          "Recovery helper must default OFF")
    check(recovery_play["pre_tasks"][0].get("delegate_to") == "localhost",
          "Recovery helper approval must be local")
    check(recovery_play["pre_tasks"][1].get("ansible.builtin.fail") is not None,
          "Old networkd rollback must remain disabled on NM-managed Pi")
    check(recovery_play["pre_tasks"][1].get("delegate_to") == "localhost",
          "Old rollback must fail on controller before SSH")


    rollback_base = ANSIBLE / "router-01" / "files"
    timer_text = (rollback_base / "router-01-lan-rollback.timer").read_text()
    service_text = (rollback_base / "router-01-lan-rollback.service").read_text()
    script_text = (rollback_base / "router-01-lan-cutover.sh").read_text()
    check("OnActiveSec=300s" in timer_text, "Five-minute rollback not set")
    check("WantedBy=timers.target" in timer_text,
          "Rollback must also survive an unconfirmed reboot")
    check("ExecStart=/usr/local/sbin/router-01-lan-cutover rollback"
          in service_text, "Rollback service must call script")
    check('systemctl enable --now "$TIMER"' in script_text,
          "Rollback timer must arm BEFORE LAN switch")
    check(script_text.find('systemctl enable --now "$TIMER"') <
          script_text.find('install -m 0644 "$NEW" "$CURRENT"'),
          "LAN switched before timer armed")
    check('systemctl -q is-active docker.service' in script_text,
          "LAN cutover must refuse Docker still running")
    check('router-01-conversion-approved' in script_text and
          'switch|confirm|rollback|status' in script_text,
          "Rollback host/command safety guard missing")
    check('networkctl reload' in script_text and
          'networkctl reconfigure "$LAN"' in script_text,
          "networkd reload + reconfigure required")

    defaults = yaml.safe_load(
        (ANSIBLE / "roles" / "router_basics" / "defaults" / "main.yml").read_text()
    )
    check(defaults["router_deploy_approved"] is False, "Unsafe default deploy gate")
    check(defaults["router_activate_services"] is False, "Unsafe default activation gate")
    check(not defaults["router_pppoe_password"], "Password must never be in Git")
    check(not defaults["router_pppoe_username"], "Username must come from off-Git vault")

    play = yaml.safe_load((ANSIBLE / "playbooks" / "router-01-basics.yml").read_text())
    check(play[0]["hosts"] == "router_staging", "Wrong play target")
    check(play[0]["vars"]["router_deploy_approved"] is False, "Play gate disabled")
    check(play[0]["vars"]["router_activate_services"] is False, "Play services must default off")
    task_text = (ANSIBLE / "roles" / "router_basics" / "tasks" / "main.yml").read_text()
    yaml.safe_load(task_text)
    check("router_conversion_approval.stat.isreg" in task_text,
          "Final router role must require approved in-place conversion")
    check("router_docker_status.stdout | trim != 'active'" in task_text,
          "Final role must refuse a running Docker daemon")
    check("policy_rc_d: 101" in task_text,
          "Final role must suppress any apt package service autostarts")
    check("masked: false" in task_text,
          "Final role must explicitly unmask services after approval")
    check("router_activate_services | bool" in task_text,
          "Final unmask must require activation approval")

    for required in (
        "ansible_facts.hostname == router_hostname_expected",
        "router_deploy_approved | bool",
        "router_expected_wan_mac",
        "router_expected_lan_mac",
        "router_activate_services | bool",
        "no_log: true",
        "router_lan_address in ansible_facts.all_ipv4_addresses",
    ):
        check(required in task_text, f"Safety task missing {required}")

    fixture = {**defaults, **conf,
               "router_pppoe_username": "example@example.invalid",
               "router_pppoe_password": "not-a-secret-fixture"}

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        undefined=StrictUndefined,
        autoescape=False,
        keep_trailing_newline=True,
    )

    with tempfile.TemporaryDirectory(prefix="router01-config-test-") as temp:
        path = pathlib.Path(temp)
        # Kea can read its config as a restricted service user in test mode.
        path.chmod(0o755)

        def render(source: str, output: str) -> pathlib.Path:
            rendered = env.get_template(source).render(**fixture)
            dest = path / output
            dest.write_text(rendered)
            dest.chmod(0o644)  # Fixtures contain no real credentials.
            return dest

        kea_path = render("kea-dhcp4.conf.j2", "kea.json")
        kea = json.loads(kea_path.read_text())["Dhcp4"]
        check(kea["interfaces-config"]["interfaces"] == ["eth0"], "Kea interface mismatch")
        subnet = kea["subnet4"][0]
        check(subnet["subnet"] == "192.168.3.0/24", "Wrong DHCP subnet")
        check(subnet["pools"][0]["pool"] == "192.168.3.100 - 192.168.3.199", "Wrong pool")
        opts = {x["name"]: x["data"] for x in subnet["option-data"]}
        check(opts == {"routers": "192.168.3.1", "domain-name-servers": "192.168.3.1"},
              "Kea must advertise router-01 as DNS and gateway")
        check("reservations" not in subnet, "Do not invent ASUS MAC/address reservations")
        # On Ubuntu CI, AppArmor can deny Kea opening a config under /tmp
        # regardless of Unix modes. Stage a non-secret fixture in /etc/kea
        # only on the disposable GitHub runner, then always remove it.
        if os.environ.get("GITHUB_ACTIONS") == "true":
            fixture_path = "/etc/kea/router-01-ci-configuration.conf"
            try:
                subprocess.run(
                    ["sudo", "-n", "install", "-m", "0644",
                     str(kea_path), fixture_path], check=True, timeout=20
                )
                subprocess.run(
                    ["sudo", "-n", "kea-dhcp4", "-t", fixture_path],
                    check=True, timeout=20
                )
                print("PASS: Kea native config validation in isolated CI")
            finally:
                subprocess.run(
                    ["sudo", "-n", "rm", "-f", fixture_path],
                    check=True, timeout=20
                )
        else:
            print("SKIP: Kea native validation outside ephemeral CI; JSON parsed")

        dns_path = render("unbound-router.conf.j2", "unbound.conf")
        dns = dns_path.read_text()
        check("interface: 192.168.3.1" in dns, "Unbound must listen on Pi LAN")
        check("access-control: 192.168.3.0/24 allow" in dns, "Wrong Unbound ACL")
        check("access-control: 0.0.0.0/0 refuse" in dns, "Open Unbound resolver risk")
        maybe_check_syntax("unbound-checkconf", [str(dns_path)])

        nft_path = render("nftables.conf.j2", "nftables.conf")
        nft = nft_path.read_text()
        check('iifname "eth0" udp sport 68 udp dport 67 accept' in nft,
              "DHCP discover (0.0.0.0) must be allowed on LAN")
        check('oifname "ppp0" ip saddr 192.168.3.0/24 masquerade' in nft,
              "Missing Pi LAN PPPoE NAT")
        check('type filter hook input priority filter; policy drop;' in nft,
              "WAN input must default deny")
        check("udp dport 67 accept" in nft, "Missing DHCP listen permission")
        maybe_check_syntax("nft", ["-c", "-f", str(nft_path)])

        peer = render("ppp-homelab-wan.j2", "peer")
        check("plugin pppoe.so" in peer.read_text(), "Wrong PPPoE plugin")
        check("nic-eth1" in peer.read_text(), "Wrong PPPoE NIC")
        check("mtu 1492" in peer.read_text(), "PPPoE MTU mismatch")
        check("lcp-echo-interval 6" in peer.read_text(), "ASUS echo interval mismatch")
        check("lcp-echo-failure 10" in peer.read_text(), "ASUS echo failure threshold mismatch")
        creds = render("ppp-secrets.j2", "ppp-secrets")
        check("not-a-secret-fixture" in creds.read_text(), "Vault templating broken")

    print("PASS: router-01 offline contract checks")
    print("Nothing contacted, installed, restarted or changed on any production device.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
