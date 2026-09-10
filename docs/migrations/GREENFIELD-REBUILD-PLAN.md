# Greenfield Rebuild Plan

**Updated:** 10 September 2026
**Status:** operating principle remains active; several major rebuilds are now complete

## Principle

The homelab may be rebuilt from clean operating systems, fresh guests or factory defaults where doing so produces a simpler and more reproducible platform than preserving historical drift.

The purpose is not to erase evidence. Existing state is captured first; persistent data and recovery material are protected; then the replacement is rebuilt from documented intent and Git/IaC.

## Rebuild rule

A host/device may be reset or reinstalled only when:

1. hardware identity and current role are recorded;
2. required persistent data is identified;
3. secrets/recovery material are protected independently;
4. rollback/recovery exists;
5. the target role/hostname is approved;
6. target configuration exists in Git/IaC where practical;
7. validation gates are written before destructive work.

## Rebuilds / role changes already completed

### Raspberry Pi 3: DietPi -> admin-01

The old physical `.48` DietPi/Pi-hole role is retired. The Pi 3 was clean-rebuilt as:

```text
admin-01.jameshouse
192.168.2.48
Debian 13
administration / SSH jump / IaC controller
```

DNS responsibility moved to the virtualized pair `.51 + .50` before `.48` became the administration host.

### ASUS ZenBook: ids-01 -> Proxmox-2

The former `ids-01` hardware has been repurposed as:

```text
Proxmox-2
192.168.2.71
standalone Proxmox VE
```

Historical ids-01 workloads are not to be restored as a general-purpose Docker stack. Current guests are `dns-01`, `monitor-01` and `edge-01`.

### Raspberry Pi 5: media-01

`media-01` is now an approved dedicated Raspberry Pi 5 Kodi/media endpoint at `192.168.2.195`, managed through Ansible.

### Monitoring

The old consolidated monitoring role has been replaced by `monitor-01` VM200 on `Proxmox-2`. Prometheus, Grafana, Alertmanager and Blackbox are live. Loki/Alloy central logging remains a fresh-build next phase.

### DNS

DNS is now split across Proxmox failure domains:

```text
dns-01 .51  CT101 on Proxmox-2
dns-02 .50  CT100 on PROXMOX
```

The old `.48` and `.242` resolver model is retired.

## Current physical-host direction

### PROXMOX / HP ProDesk

Retain the existing Proxmox installation. Do not reinstall the hypervisor merely for neatness.

Current guests:

- CT100 `dns-02`
- CT102 `mail-relay-01`
- VM200 `cloud-01`
- VM201 `sensor-01`

Priorities are guest backup/restore, storage-health documentation and capacity management rather than host reinstallation.

### Proxmox-2 / ASUS ZenBook

Keep as the secondary standalone Proxmox host.

Current guests:

- CT101 `dns-01`
- CT103 `edge-01`
- VM200 `monitor-01`

Do not assume PBS or additional workloads are automatically placed here; future guest placement still requires capacity/failure-domain review.

### Raspberry Pi 4 / TestServer

This is the next major clean rebuild.

Current:

```text
TestServer
192.168.2.220
legacy Docker / BirdNET migration source
```

Target:

```text
birdnet-01
Raspberry Pi 4
garden placement
BirdNET-Go + required management/monitoring only
```

Before reimage:

- close the TestServer backup/recovery hard gate;
- protect BirdNET configuration/data that should survive;
- remove/relocate remaining NPM/Authelia, Komodo, CI/runner, monitoring/exporter and other Docker dependencies;
- verify no production workflow/service still depends on the old host;
- update DNS/monitoring/inventory as part of the hostname cutover.

See `TESTSERVER-RETIREMENT.md`.

## Cloudflare edge build

`edge-01` is already clean-built as CT103 on `Proxmox-2` at `.56`. The base operating system is complete; `cloudflared`, tunnel registration and Access/MFA are next.

This is a service configuration phase, not another host rebuild.

## Central logging build

Build Loki/Alloy fresh on the monitoring platform. Do not preserve the TestServer or old ids-01 logging OS/container state merely to preserve historical configuration.

Initial source: validated ASUS router syslog file on `monitor-01`.

See `production docs/CENTRAL-LOGGING-SERVICE.md`.

## Network rebuild direction

### HP ProCurve

A future factory-default rebuild remains permitted if it still provides a cleaner manageable baseline.

Preserve before reset:

- management identity/address `.16`;
- cabling/port evidence;
- firmware/model details;
- VLAN/MAC information obtainable at the time;
- **port 24 as the known mirror/SPAN destination**.

Do not reset the switch merely because it is old; perform the change only when recovery/local access and required configuration intent are documented.

### ASUS router / AiMesh

A clean firmware/factory-reset rebuild remains separate planned maintenance.

Before any reset, capture WAN, DHCP, DNS, reservations, Wi-Fi/AiMesh, VPN, DDNS, port-forward and syslog state. Rebuild from documented intent rather than restoring historical drift.

Current DNS advertisement is `.51 + .50`; preserve that design after any router rebuild.

## Data migration rule

Preserve **required data and configuration**, not old operating-system state.

```text
audit current state
    -> identify authoritative data/config
    -> create/verify recovery copies
    -> build fresh target
    -> deploy from IaC
    -> restore/import required data
    -> validate
    -> retire old state
```

## Current remaining rebuild order

1. complete Cloudflare edge service configuration on already-built `edge-01`;
2. build fresh central Loki/Alloy logging on `monitor-01`;
3. finish WD 4 TB SMART review and backup/recovery design;
4. close TestServer backup/remaining-service dependencies;
5. clean-rebuild Pi 4 as `birdnet-01`;
6. complete `sensor-01` capture/Suricata/Zeek phases;
7. perform router/switch clean rebuilds only when their own recovery gates are ready;
8. continue pruning legacy repositories/branches after content equivalence is proven.

## Definition of done

A rebuilt component is complete only when:

- intended firmware/OS is installed;
- hostname/address/role match the approved architecture;
- desired configuration is represented in Git/IaC where practical;
- monitoring/central logging are appropriate for the role;
- backup/recovery exists for non-reproducible data;
- functional validation passes;
- obsolete state is retained only as long as needed for recovery/evidence;
- current architecture and runbook registry agree with the live system.
