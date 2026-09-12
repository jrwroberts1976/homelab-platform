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

The inventory currently represents these service groups:

| Group | Current members | Purpose |
|---|---|---|
| `admin_hosts` | `admin-01` | Administration / IaC controller |
| `dns_resolvers` | `dns-01`, `dns-02` | Pi-hole + Unbound recursive DNS |
| `proxmox_hosts` | `PROXMOX`, `Proxmox-2` | Standalone Proxmox VE hosts |
| `proxmox_time_servers` | `PROXMOX`, `Proxmox-2` | Redundant LAN Chrony/NTP service |
| `monitoring_hosts` | `monitor-01` | Prometheus, Grafana, Alertmanager and Blackbox |
| `cloud_hosts` | `cloud-01` | Nextcloud private-cloud stack |
| `mail_relay` | `mail-relay-01` | Internal Postfix notification relay |
| `edge_hosts` | `edge-01` | Cloudflare Tunnel edge connector |
| `sensor_hosts` | `sensor-01` | Suricata/Zeek security sensor platform |
| `media_hosts` | `media-01` | Raspberry Pi 5 Kodi endpoint |
| `birdnet_hosts` | `docker-01` | Raspberry Pi 4 BirdNET-Go Docker host |

Current DNS service addresses are `dns-01` at `192.168.2.51` and `dns-02` at `192.168.2.50`. The former DNS role at `192.168.2.48` has been retired; `.48` is now `admin-01` and must not be documented or configured as a resolver.

## Main playbooks

| Playbook | Purpose |
|---|---|
| `proxmox-time.yml` | Configure both Proxmox hosts as Chrony/NTP servers |
| `proxmox-resolver.yml` | Reconcile resolver configuration on both Proxmox hosts |
| `dns-resolver.yml` | Configure a reusable Pi-hole + Unbound resolver |
| `dns-02.yml` | Legacy/specific entry point for the `dns-02` resolver build |
| `dns-local-records.yml` | Reconcile managed Pi-hole local DNS records |
| `monitoring.yml` | Reconcile the central Prometheus/Grafana/Alertmanager/Blackbox stack |
| `node-exporters.yml` | Reconcile Node Exporter on the groups covered by that playbook |
| `router-syslog.yml` | Reconcile the ASUS remote syslog receiver on `monitor-01` |
| `cloud-01.yml` | Reconcile the `cloud-01` operating-system baseline |
| `cloud-01-storage.yml` | Reconcile the dedicated `cloud-01` data filesystem |
| `cloud-stack.yml` | Reconcile Nextcloud, PostgreSQL, Redis and cron |
| `mail-relay.yml` | Reconcile the Postfix relay service |
| `media-01.yml` | Reconcile the Kodi media endpoint |
| `birdnet-01.yml` | Reconcile the BirdNET-Go Docker host |
| `network-sensor.yml` | Reconcile the sensor toolchain |
| `network-sensor-config.yml` | Reconcile guarded Suricata/Zeek configuration |

Preflight playbooks and scripts should be used where supplied before an initial build or a potentially disruptive infrastructure change.

## Standard validation sequence

For an ordinary existing-service change:

```bash
cd ~/projects/homelab-platform/IaC/ansible

ansible-playbook --syntax-check playbooks/<playbook>.yml
ansible-playbook --check playbooks/<playbook>.yml
ansible-playbook playbooks/<playbook>.yml
ansible-playbook playbooks/<playbook>.yml
```

Check mode is not a substitute for understanding the playbook. Some initial-build workflows intentionally cannot complete meaningfully in check mode because later validation depends on packages/services created earlier in the same real run. Follow the service-specific preflight or wrapper in those cases.

A stable second real reconciliation should normally report `changed=0`, with `unreachable=0` and `failed=0`.

## Production Nextcloud

`cloud-01` is a production deployment, not a staging instance. Its application role has two deliberate safety controls:

1. it verifies `/srv/cloud-01-data` is the approved dedicated ext4 `drive-scsi1` filesystem mounted read-write;
2. a real application reconciliation is refused unless `cloud_stack_allow_deploy=true` is explicitly supplied.

The preferred controller entry point is:

```bash
cd ~/projects/homelab-platform
bash IaC/scripts/deploy-cloud-stack.sh
```

The wrapper loads protected secrets, validates the dedicated data filesystem, performs syntax/check-mode validation, runs the explicitly approved reconciliation, proves idempotence and checks the live Nextcloud status endpoint.

For direct Ansible use, first load the protected `cloud-01.env`, then the real apply requires:

```bash
ansible-playbook playbooks/cloud-stack.yml -e cloud_stack_allow_deploy=true
```

Do not remove or bypass either the storage gate or the explicit deployment gate.

## DNS model

Both resolvers are Proxmox LXCs and use Pi-hole + Unbound:

- `dns-01.jameshouse` -> `192.168.2.51`
- `dns-02.jameshouse` -> `192.168.2.50`

Unbound performs recursive resolution and DNSSEC validation; Pi-hole provides policy/blocking and local DNS. Resolver builds must be validated directly before any DHCP/client cutover. The approved resolver pair is `.51` and `.50`; the old `.48`/`.242` resolver identities are historical only.

`playbooks/proxmox-resolver.yml` also keeps the physical Proxmox hosts on the current `.51` / `.50` resolver pair.

## Time service

`playbooks/proxmox-time.yml` configures:

- `ntp-01.jameshouse` -> `PROXMOX` / `192.168.2.70`
- `ntp-02.jameshouse` -> `Proxmox-2` / `192.168.2.71`

Chrony runs on the physical hypervisors so LAN time does not depend on a guest. Proxmox LXCs inherit host time; supported VM/physical clients use the `chrony_client` role where applicable.

## Protected configuration

Production secret values are not stored in Git. Controller-side protected files currently include, as applicable:

```text
~/.config/homelab-iac/proxmox.env
~/.config/homelab-iac/mail-relay.env
~/.config/homelab-iac/cloud-01.env
~/.config/homelab-iac/monitoring.env
```

Pi-hole credentials are supplied through the approved runner environment/workflow secret path. SSH automation keys live under `~/.ssh/` and are referenced by inventory; private keys must never be committed.

Do not print secret values into chat, CI logs, shell history or validation reports.

## Monitoring coverage

The central monitoring stack is live on `monitor-01`, but observability standardisation is still an active workstream. The current Prometheus target lists do not yet imply complete coverage of every host in the Ansible inventory. Expand monitoring through reviewed IaC and validate new targets before treating missing telemetry as a host/service failure.

`IaC/scripts/deploy-node-exporters.sh` derives its expected Prometheus Node Exporter target count from the monitoring role defaults so its validation cannot silently drift from the configured target list.

## Safety notes

- Keep host-key checking enabled for normal runs.
- Do not use `ANSIBLE_HOST_KEY_CHECKING=False` as a routine workaround; it is reserved for tightly controlled first-boot/bootstrap flows that independently verify identity.
- Do not convert current production guests into “fresh builds” just because a bootstrap script exists.
- Keep destructive storage operations behind device identity, size and explicit-approval gates.
- Preserve accepted production data when reconciling Terraform state.
- Validate failed systemd units, application health and service reachability after a real change.
