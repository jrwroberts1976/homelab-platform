#!/usr/bin/env python3
"""Preview-first, presentation-only KVM guest label update.

Guest identities come from the operator's 2026-11-10 read-only Ansible
virtualization fact audit (role=guest, type=kvm). Never infer guests from
virtualization_type alone: physical KVM-capable hosts also report type=kvm.
"""
import argparse
import copy
import hashlib
import importlib.util
import re
from importlib.machinery import SourceFileLoader
from pathlib import Path

BUILDER = Path("/usr/local/sbin/homelab-grafana-zabbix-rebuild")
KVM_GUESTS = ("cloud-01", "greenbone-01", "monitor-01", "sensor-01")
EXPECTED_NON_GUESTS = {
    "PROXMOX", "Proxmox-2", "admin-01", "media-01",
    "dns-01", "dns-02", "edge-01", "komodo-01",
    "mail-relay-01", "zabbix-01", "router-01",
}


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    loader = SourceFileLoader("homelab_zabbix_rebuild", str(BUILDER))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    z = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(z)
    names, _, headers = z.read_secret_files()
    require(len(names) == 15 and set(names) == set(KVM_GUESTS) | EXPECTED_NON_GUESTS,
            "Managed host inventory changed; review guest classification before proceeding")

    plans = []
    for name in KVM_GUESTS:
        uid = "zbx-host-" + hashlib.sha256(name.encode()).hexdigest()[:20]
        resp = z.grafana_api(headers, "/api/dashboards/uid/" + uid)
        dash = resp["dashboard"]
        require(dash.get("uid") == uid and dash.get("title") == name
                and z.MARKER in dash.get("tags", [])
                and resp.get("meta", {}).get("folderUid") == "homelab-managed-devices",
                "Unrecognised dashboard identity: " + name)
        panels = dash.get("panels", [])
        matches = [p for p in panels if p.get("id") == 95]
        require(len(matches) == 1, "Missing/duplicate kernel panel: " + name)
        panel = matches[0]
        require(panel.get("type") == "text"
                and panel.get("title") in ("Kernel", "Kernel / Virtualisation")
                and panel.get("options", {}).get("mode") == "markdown",
                "Unexpected kernel panel layout: " + name)
        value = panel["options"].get("content", "")
        require(bool(re.fullmatch(r"`[^`\r\n]{1,150}`", value))
                or bool(re.fullmatch(r"`[^`\r\n]{1,150}` · \*\*KVM\*\*", value)),
                "Unexpected kernel panel content: " + name)
        already = panel.get("title") == "Kernel / Virtualisation" and value.endswith(" · **KVM**")
        require(not (panel.get("title") == "Kernel / Virtualisation" and not already),
                "Existing virtualisation label drift: " + name)
        require(not (panel.get("title") == "Kernel" and value.endswith(" · **KVM**")),
                "Partially migrated kernel label: " + name)
        candidate = copy.deepcopy(dash)
        new_panel = next(p for p in candidate["panels"] if p.get("id") == 95)
        if not already:
            new_panel["title"] = "Kernel / Virtualisation"
            new_panel["options"]["content"] = value + " · **KVM**"
        before = {p["id"]: p for p in panels}
        after = {p["id"]: p for p in candidate["panels"]}
        require(len(before) == len(panels)
                and len(after) == len(candidate["panels"])
                and set(before) == set(after),
                "Panel inventory changed: " + name)
        for pid in before:
            if pid != 95:
                require(before[pid] == after[pid],
                        "Unrelated panel changed: " + name + ":" + str(pid))
        plans.append((name, candidate, already))
        print(("PLAN EXISTS: " if already else "PLAN UPDATE: ") + name + " kernel + KVM guest label")

    print("KVM GUARD: 4 verified KVM guests; 11 other dashboards protected; kernel version retained")
    print("PLAN SUMMARY: " + str(sum(not already for _, _, already in plans)) + " dashboard updates")
    if not args.apply:
        print("AUDIT ONLY: no Grafana API writes")
        return
    for name, dash, already in plans:
        if already:
            continue
        z.grafana_api(headers, "/api/dashboards/db", "POST", {
            "dashboard": dash, "folderUid": "homelab-managed-devices",
            "overwrite": True, "message": "Label confirmed KVM guest; retain kernel version",
        })
        print("APPLIED UPDATE: " + name)
    print("APPLY SUMMARY: " + str(sum(not already for _, _, already in plans)) + " dashboard updates")


if __name__ == "__main__":
    main()
