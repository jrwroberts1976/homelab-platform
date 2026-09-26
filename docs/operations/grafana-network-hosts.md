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

## Saved Nmap OS fingerprints (optional, no-scan evidence integration)

The read-only Nmap fingerprint publisher and monitor-01 correlation were
deployed on 2026-09-26. The deep-profiler scan timer is **not** enabled by
this integration. The first deployment exported 0 matches because the older
saved profile records do not contain the newer per-TCP `tcp_scanned_at`
field—not because no OS fingerprints were collected.

Proxmox-2 stores root-only, MAC-keyed completed/partial scan results in
`/var/lib/homelab-network-hosts/deep-profiles.json`. The standalone
`homelab-network-os-evidence.service` reads **only that existing JSON**,
publishes a minimised metric through Proxmox-2 node exporter and runs on an
independent five-minute timer. **It does not invoke Nmap, enable the scanner,
run UDP scans, or alter existing scan state.**

On `monitor-01`, the inventory correlator reads the exported
`homelab_network_host_os_fingerprint_info` metric. A result is eligible
**only when the recorded scan MAC and scanned IP both match the device's
current inventory**; an old fingerprint from a reassigned DHCP IP must not
be attributed to a new device. The oldest baseline scan remains a
lower-priority clue. Documented OS and previously curated DNS-derived OS
are not silently overwritten by Nmap guesses.

The individual host generator adds the panel
**Nmap OS fingerprint — inferred evidence** *only* if a correlated match
exists. It displays the raw Nmap match, Nmap-reported match accuracy,
OS family, generation, vendor, CPE (when supplied), the best available
**recorded evidence time and its basis**, complete/partial scan status
and a bounded summary of positively observed open TCP services. Do not interpret Nmap's reported accuracy as a
probability of correctness; retained guesses always remain `inferred_nmap`.

If there is no saved fingerprint, the saved time is explicitly invalid,
a scan timed out, or the current MAC/IP does not match the saved identity,
the fingerprint panel does not appear.
An absent panel is not proof that an OS is unknown or that a host has no
open ports. The "OS to investigate" counter continues to include unknown
and inferred OS identifications until independently documented.

### Deploy the read-only Nmap integration

After merging this PR, from `admin-01` check out the **merged** commit
into a fresh worktree and run:

```bash
REPO=/home/james/projects/homelab-platform
DEPLOY=/var/tmp/network-host-os-evidence
git -C "$REPO" fetch origin main
git -C "$REPO" worktree add --detach "$DEPLOY" origin/main
cd "$DEPLOY/IaC/ansible"
ansible-playbook -i inventory/hosts.yml \
  playbooks/network-host-os-fingerprints.yml --syntax-check
ansible-playbook -i inventory/hosts.yml \
  playbooks/network-host-os-fingerprints.yml
```

The first play requires the **existing** deep-profile JSON on Proxmox-2,
publishes current evidence, and enables only the read-only export timer.
The second installs the updated monitor-01 correlation and dashboard
generator, waits for Prometheus scrapes, regenerates host pages, and
restarts Grafana only when the dashboard assets actually change. It
reports both the exported fingerprint count and the count that matched
current MAC/IP identities. An exported count of zero does **not** prove
that no OS fingerprint was collected: inspect the read-only profile state
and check legacy schemas or missing identity fields before proposing
another scan. The playbook must not invent timestamps or launch new scans.

To inspect read-only export status on Proxmox-2:

```bash
systemctl status homelab-network-os-evidence.timer --no-pager
journalctl -u homelab-network-os-evidence.service -n 25 --no-pager
grep -c '^homelab_network_host_os_fingerprint_info{' \
  /var/lib/prometheus/node-exporter/homelab_network_os_fingerprints.prom
```

### Legacy OS profile timestamps and recovered evidence

On 2026-09-26, a read-only check of the existing Proxmox-2 profile state
found **49 device records**: 35 baseline, 13 complete and 1 pending.
Thirteen records contained TCP scan data, **eight contained Nmap OS
matches**, and none contained the newer `profile.tcp_scanned_at` field.
The original exporter inadvertently dropped all eight when enforcing that
new timestamp, so the first integration published zero matches despite
usable historical OS evidence.

The compatible exporter reads **existing timestamps only**, in order:
`profile.tcp_scanned_at` (exact TCP scan time),
`profile.scanned_at` (older recorded scan time), then
`record.profiled_at` (profile completion, **not an exact TCP scan time**).
The per-host Grafana table now shows **Time source** so those distinctions
are visible. When none of those recorded timestamps exists but the Nmap
match, source MAC and scanned IP are valid, the table explicitly says
**Not recorded / Unknown** instead of discarding the match or inventing a
date. Malformed or future recorded dates are rejected unless a separate,
valid recorded timestamp exists.

This change recovers up to eight existing Nmap OS matches; the final count
actually shown in Grafana may be lower if some saved records do not match
both the device's **current MAC and scanned IP**. IP reassignment is not
assumed safe. Nmap match confidence remains the tool's own reported score,
never an independently verified probability or an OS confirmation.

For the compatibility rollout use the separate worktree
`/var/tmp/network-host-os-legacy-time-fix` to avoid colliding with the
already deployed `/var/tmp/network-host-os-evidence` worktree. Check out
the merged commit from `origin/main` and rerun only the focused playbook
`IaC/ansible/playbooks/network-host-os-fingerprints.yml`.
