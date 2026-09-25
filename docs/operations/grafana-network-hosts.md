# Grafana network hosts — data-only dashboards

## Visible dashboards

**Homelab — Network Hosts** is now a compact selector and device directory.
**Homelab — Host Detail** is an intentionally minimal, hostname-selected
record showing status, operating-system identification, port summary and
available DNS evidence. Neither shared dashboard displays blank Linux CPU,
memory, patch or filesystem panels for a device like a router or smart camera.

The **Full Host Dashboard** navigation link on either shared dashboard
resolves the currently selected hostname's stable generated Grafana dashboard
UID. All dashboards show hostnames, or the IP address when a hostname is
unknown; MAC addresses remain hidden internal identity keys so DHCP address
changes do not create duplicate per-device dashboards.

## Individual host pages: include data only

The **Network Hosts** Grafana folder contains automatically generated
per-device dashboards. The five-minute generator checks Prometheus for the
device's *recorded data during the default last-24-hour window* and publishes
only the relevant panels:

- Always: hostname, current IP, known OS/evidence and the observed-port summary.
- If observed: online state/history and last-seen time.
- If measured: observed-open-port count and the actual per-port service table.
- If present: concise DNS evidence. The currently curated DNS clues were
  observed 18–25 September 2026, not continuously collected.
- If the host exports real Linux telemetry: only the measured CPU, memory,
  network, filesystem, disk, load and patching panels for which Prometheus
  contains samples. A *genuine zero updates* reading counts as data.
- Live OS facts only when exported.

The generator does not create a large **ONLINE** tile or insert placeholder
graphs and text banners. It rearranges the existing compact Grafana panels
without leaving blank rows. For a typical router, this should give a short
status/evidence/ports page; for an actively monitored Linux host, the familiar
Production Hosts charts remain available.

Missing Nmap records, timed-out scans or empty port evidence are **unknown**,
never proofs of closed ports. DNS and Nmap operating-system guesses remain
separate from documented operating-system facts. Linux data is checked via
Prometheus, not inferred from a hostname or DNS traffic.

## Change control and deployment

The shared dashboard JSON is mirrored in the Ansible and Komodo trees:

- `IaC/ansible/roles/monitoring_stack/files/grafana/dashboards/`
- `IaC/komodo/stacks/monitoring/grafana/provisioning/dashboards/homelab/`

The full auto-generated profile template is stored separately in
`IaC/ansible/roles/monitoring_stack/files/host-profile-template.json`.
It is **not** provisioned as a static dashboard; the generator chooses and
lays out real-data panels from it for each device.

The focused deployment playbook copies only the two compact static dashboards,
the full generator template and existing exporter/generator scripts. It
doesn't redeploy Prometheus or the other monitoring containers:

```bash
cd /home/james/projects/homelab-platform
git fetch origin main
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/network-host-grafana.yml --syntax-check
ansible-playbook -i inventory/hosts.yml \
  playbooks/network-host-grafana.yml
```

Verify `homelab_network_device_card_info` on monitor-01's Prometheus,
then open **Homelab — Network Hosts** and a few generated host pages,
including a Linux host and an unmanaged router. Generated JSON files live
under `/opt/monitoring/grafana/provisioning/dashboards/network-hosts/`.
Grafana's file provider checks for changed JSON every 30 seconds.
