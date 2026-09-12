# Ansible service configuration

This directory is the configuration authority for the homelab hosts and services represented in `inventory/hosts.yml`.

The normal controller is `admin-01` (`192.168.2.48`). Run production Ansible from the checked-out `homelab-platform` repository on that host unless a recovery runbook explicitly specifies another controller.

## Controller setup

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-inventory --graph
ansible all --list-hosts
```

`ansible.cfg` enables host-key checking and uses `inventory/hosts.yml` plus the local `roles/` directory. Unknown or changed SSH host keys must be validated rather than bypassed during normal operation.

## Current inventory groups

| Group | Current members | Purpose |
|---|---|---|
| `admin_hosts` | `admin-01` | Administration / IaC controller |
| `dns_resolvers` | `dns-01`, `dns-02` | Pi-hole + Unbound recursive DNS |
| `proxmox_hosts` | `PROXMOX`, `Proxmox-2` | Standalone Proxmox VE hosts |
| `proxmox_time_servers` | `PROXMOX`, `Proxmox-2` | Redundant LAN Chrony/NTP service |
| `monitoring_hosts` | `monitor-01` | Prometheus, Grafana, Alertmanager and Blackbox |
| `cloud_hosts` | `cloud-01` | Nextcloud private-cloud stack |
| `mail_relay` | `mail-relay-01` | Internal Postfix notification relay |
| `edge_hosts` | `edge-01` | Reserved edge host; Cloudflare Tunnel application not deployed |
| `sensor_hosts` | `sensor-01` | Suricata/Zeek platform; capture phase pending |
| `media_hosts` | `media-01` | Raspberry Pi 5 Kodi endpoint |
| `birdnet_hosts` | `docker-01` | Raspberry Pi 4 BirdNET-Go Docker host |

Inventory group membership describes intended management scope. It does not by itself prove an application is deployed. In particular, `edge-01` is a healthy LXC but `cloudflared` is not currently installed/running.

Current DNS addresses:

```text
dns-01 -> 192.168.2.51
dns-02 -> 192.168.2.50
```

The former DNS role at `192.168.2.48` has been retired; `.48` is `admin-01` and must not be configured as a resolver.

## Main playbooks

| Playbook | Purpose |
|---|---|
| `proxmox-time.yml` | Configure both Proxmox hosts as Chrony/NTP servers |
| `proxmox-resolver.yml` | Reconcile resolver configuration on both Proxmox hosts |
| `dns-resolver.yml` | Configure a reusable Pi-hole + Unbound resolver |
| `dns-02.yml` | Legacy/specific entry point for the `dns-02` resolver build |
| `dns-local-records.yml` | Reconcile managed Pi-hole local DNS records |
| `monitoring.yml` | Reconcile Prometheus/Grafana/Alertmanager/Blackbox |
| `node-exporters.yml` | Reconcile Node Exporter on covered groups |
| `router-syslog.yml` | Reconcile ASUS remote syslog receiver on `monitor-01` |
| `cloud-01.yml` | Reconcile the `cloud-01` OS baseline |
| `cloud-01-storage.yml` | Reconcile the dedicated `cloud-01` data filesystem |
| `cloud-stack.yml` | Reconcile Nextcloud, PostgreSQL, Redis and cron |
| `mail-relay.yml` | Reconcile the Postfix relay service |
| `media-01.yml` | Reconcile the Kodi media endpoint |
| `birdnet-01.yml` | Reconcile BirdNET-Go on target host `docker-01` |
| `network-sensor.yml` | Reconcile the sensor toolchain |
| `network-sensor-config.yml` | Reconcile guarded Suricata/Zeek configuration |

The `birdnet-01.yml` filename is retained as an implementation interface; its current inventory target is `docker-01`.

## Standard validation sequence

For an ordinary existing-service change:

```bash
cd ~/projects/homelab-platform/IaC/ansible

ansible-playbook --syntax-check playbooks/<playbook>.yml
ansible-playbook --check playbooks/<playbook>.yml
ansible-playbook playbooks/<playbook>.yml
ansible-playbook playbooks/<playbook>.yml
```

Check mode is not a substitute for understanding the playbook. Some bootstrap workflows intentionally cannot complete meaningfully in check mode because later validation depends on resources created earlier in the same run.

A stable second real reconciliation should normally report `changed=0`, `unreachable=0` and `failed=0`.

## Production Nextcloud

`cloud-01` is production, not staging.

The application role has deliberate safety controls:

1. verify `/srv/cloud-01-data` is the approved dedicated ext4 data filesystem;
2. refuse a real application reconciliation unless the explicit deployment gate is supplied.

Preferred entry point:

```bash
cd ~/projects/homelab-platform
bash IaC/scripts/deploy-cloud-stack.sh
```

Do not bypass the storage or explicit-deployment gates.

## DNS model

Both resolvers are Proxmox LXCs using Pi-hole + Unbound.

Unbound performs recursion/DNSSEC validation; Pi-hole provides policy/blocking and local DNS. Resolver builds must be validated directly before any DHCP/client cutover.

Known current parity defect: `dns-02` does not currently return the `dns-01.jameshouse` local record because the base managed host list includes `dns-02` but not the cross-record for `dns-01`. Correct that in a separate reviewed IaC change rather than through manual GUI drift.

## Time service

`playbooks/proxmox-time.yml` configures:

```text
ntp-01.jameshouse -> PROXMOX / 192.168.2.70
ntp-02.jameshouse -> Proxmox-2 / 192.168.2.71
```

Chrony runs on the physical hypervisors so LAN time does not depend on a guest.

## Sensor state

`sensor-01` Phase 1 is deployed and validated. Suricata/Zeek are installed but deliberately stopped because the dedicated capture NIC/SPAN path does not yet exist.

Do not alter the guarded capture-interface configuration simply to make services run before the physical capture path is ready.

## Protected configuration

Production secret values are not stored in Git. Controller-side protected files include, as applicable:

```text
~/.config/homelab-iac/proxmox.env
~/.config/homelab-iac/proxmox-pve2.env
~/.config/homelab-iac/pihole.env
~/.config/homelab-iac/mail-relay.env
~/.config/homelab-iac/cloud-01.env
~/.config/homelab-iac/monitoring.env
```

SSH automation/recovery keys live under `~/.ssh/` and are referenced by the approved workflows. Private keys and secret values must never be committed or printed into chat, CI logs, shell history or validation reports.

## Monitoring coverage

The central monitoring stack is operational on `monitor-01`.

The 12 September audit found 23 active Prometheus targets, all healthy, and zero active alerts. Current target lists still do not imply complete service-level observability for every inventory host.

`IaC/scripts/deploy-node-exporters.sh` derives its expected Node Exporter target count from the monitoring role defaults to reduce silent drift.

## Safety notes

- Keep host-key checking enabled for normal runs.
- Do not use `ANSIBLE_HOST_KEY_CHECKING=False` as a routine workaround.
- Do not convert current production guests into “fresh builds” merely because a bootstrap script exists.
- Keep destructive storage operations behind device identity, size and explicit-approval gates.
- Preserve accepted production data when reconciling Terraform state.
- Validate failed systemd units, application health and service reachability after a real change.
- Documentation reconciliation alone does not authorise infrastructure changes.
