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
