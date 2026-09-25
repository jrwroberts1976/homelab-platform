# Grafana network hosts — hostname-first operational view

The native Grafana **Homelab — Network Hosts** dashboard uses the layout of
the existing Production **Homelab — Hosts** view: a **Host** dropdown, four
compact CPU/memory/patch status panels, CPU and memory graphs, then network
and filesystem graphs. Below those are the selected device's network presence,
OS classification and evidence, positively observed open ports, DNS clues and
a browsable directory of other hosts.

## URLs

- Network Hosts (hostname selector):
  `http://192.168.2.52:3000/d/homelab-network-host-tiles`
- Generic Host Detail (hostname selector):
  `http://192.168.2.52:3000/d/homelab-mac-device-detail`
- Automatically generated per-device dashboards: Grafana's **Network Hosts**
  folder. Each dashboard's visible title is `Homelab — <hostname>`.

The *visible* identity is the hostname, with IP fallback where there is no
reliable hostname. Duplicate friendly hostnames are disambiguated with the IP.
MAC addresses remain **internal stable keys** for the collection pipeline and
the generated dashboard UID, so an IP change doesn't create a new device page.
They are hidden from host selectors, titles and the main data tables.

## Telemetry and evidence limitations

- CPU, memory, network throughput, filesystem and patch panels reuse the
  deployed Linux Node Exporter metrics. Phones, IoT appliances and other
  unmanaged hosts generally show **No telemetry** in these panels rather
  than fake zeros or invented performance data.
- OS is marked as **documented** from the canonical estate or explicitly
  **inferred_dns** / **inferred_nmap** where there is only supporting evidence.
  DNS hints are the 18–25 September 2026 snapshot, **not** continuous DNS
  collection. AI-assisted ongoing classification is not deployed by this
  dashboard change.
- Open ports are **positively observed open** services from limited scans.
  Missing data, Nmap timeouts and unscanned hosts do **not** mean closed ports.
- The 5-minute textfile publisher maintains both the older inventory metrics
  and the MAC-keyed `homelab_network_device_card_*` metrics. The dashboard
  generator uses those to create and refresh individual native Grafana JSON
  dashboards. It doesn't perform a new LAN scan.

## Git-owned deployment

The Ansible and Komodo static JSON copies are deliberately mirrored:

- `IaC/ansible/roles/monitoring_stack/files/grafana/dashboards/`
- `IaC/komodo/stacks/monitoring/grafana/provisioning/dashboards/homelab/`

For the existing `monitor-01` deployment, the focused rollout only installs
the dashboard files, publisher, generator and Grafana provider, rather than
reconciling the whole Docker monitoring stack:

```bash
cd /home/james/projects/homelab-platform
git fetch origin main
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml playbooks/network-host-grafana.yml --syntax-check
ansible-playbook -i inventory/hosts.yml playbooks/network-host-grafana.yml
```

When applying from a deployment worktree instead, run this from that worktree's
`IaC/ansible` directory. A successful rollout should create at least ten
`net-host-*.json` files in the **Network Hosts** provisioning directory.
If Grafana remains on the older layout after a deploy, verify the dashboard
UID and file-provider polling or Grafana restart before editing dashboards
through the UI.
