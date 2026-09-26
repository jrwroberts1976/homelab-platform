# Network Hosts — recreated legacy Grafana workflow (2026-09)

This implementation recreates the **behaviour** documented by the retired
`home-lab-docs/network-discovery-dashboard.md`. The historical generator and
generated JSON were deleted; this is a new implementation using the present
authoritative infrastructure rather than restoring retired hosts or scans.

## Use the dashboard

Open [Homelab — Network Hosts](http://192.168.2.52:3000/d/homelab-network-host-tiles).
It is the discovery **directory**, not a fixed panel-heavy device dashboard.

- Four network-wide summaries: known, online, documented OS and OS that still
  needs investigation.
- Choose a **hostname** in the dropdown to inspect identity, OS evidence,
  recorded open ports and curated DNS clues.
- The directory shows the current IP and one **Open host →** link per device.
  Click it to open **that device's own Grafana JSON dashboard**. Alternatively,
  use **Individual hosts** at the top: Grafana lists the generated host titles.
- Generated dashboards are grouped in Grafana's **Network Hosts** folder and
  provide a **Choose host** dropdown for switching to another *different*
  device dashboard. The ordinary fixed Host dropdown on the landing page
  does not attempt to hide or alter panels dynamically.

Hostnames (IP fallback when unknown) are shown to humans. MACs remain an
internal stable identity key: the generated dashboard's `net-host-<digest>`
UID and file name do not change when DHCP changes the IP or a hostname is
enriched later. Duplicate friendly names are disambiguated with the IP.

## Panels are decided by actual recorded data

The generator uses the current 24-hour Prometheus history and published
`homelab_network_device_card_*` series. It starts from the existing
Production Hosts-inspired layout but **only includes panels for data that
really exists on this individual host**.

| Host situation | What is generated |
|---|---|
| ASUS router or AiMesh node without Node Exporter | Identity, presence, last-seen (when known), OS/evidence, positively observed open ports and relevant DNS hints. **No CPU, memory, patching or filesystem panels.** |
| `sensor-01` or another Linux host with telemetry | The same device/network details, **plus only** CPU, memory, disk, network, patching and filesystem panels whose relevant metrics have samples. A measured **zero** security updates remains a valid value and its panel remains. |
| Camera, phone, disconnected IoT | Only observed presence, identity, ports (if scanned) and DNS clues (if observed). No blank panels for uncollected measurements. |

Source-specific limitations are visible: authoritative OS from the
`IaC/inventory/estate.json` inventory, separate DNS- and Nmap-inferred OS,
and observed open ports from **limited** scans. An empty port record or timed
out Nmap scan is **not** proof that the device has no open ports.
Current curated DNS clues are a dated **18–25 September 2026 snapshot** from
`dns-01` and `dns-02`; continuous DNS/AI analysis is *not* deployed by
this dashboard.

## Restored two-loop architecture

The legacy implementation used independent inventory and dashboard
generation loops. The new deployment follows the same separation:

```text
Current ASUS router inventory + current monitoring discovery
  + canonical IaC estate + dated, minimised dns-01/dns-02 clues
  + usable selective Nmap observations
            |
            v
homelab-network-device-inventory.timer  (5 min)
            |
            v
/var/lib/prometheus/node-exporter/homelab_network_devices.prom
            |
            v
Node Exporter -> Prometheus on monitor-01
            |
            v
homelab-network-host-dashboards.timer (first run 2 min after activation,
                                      then every 5 min)
            |
            v
network-host-dashboard-generator.py
  checks current inventory and real telemetry samples
  chooses and compacts only applicable panels per device
            |
            v
/opt/monitoring/grafana/provisioning/dashboards/network-hosts/net-host-*.json
            |
            v
Grafana file provider -> Network Hosts folder
```

The collector does **not** run a new broad Nmap scan to create dashboards.
The collector's systemd service can write *only* its Prometheus textfile
directory; a dedicated generator service has the separate, narrowly-scoped
permission to write generated Grafana JSON. A failed dashboard-generator run
does not destroy the previous good dashboard set.

## Deployment from admin-01

Merge the corresponding GitHub PR first. Then check out the exact merged
commit from `origin/main` in a separate worktree and run the **focused**
playbook. This only changes the dashboard publisher, generator, provider and
provisioned host dashboards; it does not recreate the other monitoring
containers.

```bash
REPO=/home/james/projects/homelab-platform
git -C "$REPO" fetch origin main
DEPLOY=/var/tmp/network-host-dashboard-rebuild
git -C "$REPO" worktree add --detach "$DEPLOY" origin/main
cd "$DEPLOY/IaC/ansible"
ansible-playbook -i inventory/hosts.yml \
  playbooks/network-host-grafana.yml --syntax-check
ansible-playbook -i inventory/hosts.yml \
  playbooks/network-host-grafana.yml
```

The playbook validates `monitor-01` identity, publishes current evidence,
generates the dashboard files, verifies that the *actual running Grafana
container* sees the updated JSON and at least ten generated pages, and checks
the authenticated **live Grafana API**. The latter explicitly requires the
seven-panel rebuilt directory and at least ten indexed tagged per-host
dashboards; an old cached dashboard does not count as deployment success.
Credentials are read from the existing protected runtime `.env` and are
not printed or committed.

## Troubleshooting on monitor-01

```bash
systemctl status homelab-network-device-inventory.timer \
  homelab-network-host-dashboards.timer --no-pager
journalctl -u homelab-network-host-dashboards.service -n 35 --no-pager
find /opt/monitoring/grafana/provisioning/dashboards/network-hosts \
  -maxdepth 1 -type f -name 'net-host-*.json' | wc -l
```

If the generator succeeds but the old page still renders, compare the
dashboard JSON seen by Grafana with the host-side file and check the live
`/api/dashboards/uid/homelab-network-host-tiles` response. Do not
repeatedly rerun the entire monitoring-stack playbook or hand-edit
provisioned Grafana dashboards in the web UI.
