<!-- estate-authority: IaC/inventory/estate.json -->
# Homelab Greenbone Vulnerability Scanner Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** OPERATIONAL — LAN-ONLY SCANNER / AUTOMATED EVIDENCE SOURCE  
**Host:** `greenbone-01.jameshouse`  
**IPv4:** `192.168.2.57`  
**Placement:** VM203 on `Proxmox-2`  
**Last current-state review:** 6 October 2026

## Purpose

`greenbone-01` provides active vulnerability scanning for approved homelab targets.

It complements `sensor-01` rather than replacing it:

- `sensor-01` performs passive Suricata/Zeek observation;
- `greenbone-01` performs active vulnerability assessment;
- both feed separate evidence into central reporting.

## Platform

```text
VMID:       203
name:       greenbone-01
node:       Proxmox-2
IPv4:       192.168.2.57
vCPU:       4
RAM:        8192 MiB
disk:       80 GiB local-lvm
protection: enabled
OS:         Debian 13
```

Greenbone Community Containers run through Docker Compose. Upstream rolling tags are runtime inputs, not immutable appliance versions.

## Exposure

Approved exposure is LAN/VPN only:

```text
192.168.2.57:443  Greenbone HTTPS
```

There is no approved public/Cloudflare exposure. The current certificate is self-signed unless separately replaced.

## Feed / commissioning state

Commissioning required all feed families ready and a controlled self-scan. Historical commissioning evidence recorded no Critical/High/Medium findings and one Low ICMP timestamp observation.

Current vulnerability management is not limited to that commissioning scan: recurring managed scans and central evidence handling are operational.

## Automated scan and evidence workflow

Current production workflow:

```text
02:00 local
  greenbone-01 managed scan
        |
        v
/var/lib/homelab-greenbone-scanning/managed.json
        |
        | restricted SSH/SFTP evidence transfer
        v
monitor-01 evidence store
        |
        v
schema/freshness validation
        |
        v
06:00 management report / AI-assisted summary / mail delivery
```

Key controls:

- `homelab-greenbone-managed-scan.timer` runs the managed scan daily;
- local `flock` and Greenbone task-state guards prevent overlapping managed scans;
- evidence is schema-validated and freshness-checked;
- the evidence freshness threshold is 30 hours;
- missing/invalid/stale evidence is reported as an evidence problem, never as zero vulnerabilities;
- evidence transfer uses a dedicated restricted identity/key and pinned receiver host key;
- numeric vulnerability counts remain deterministic source evidence rather than AI-generated values.

## Monitoring and logging

Current host observability includes:

- Node Exporter;
- Grafana Alloy;
- Zabbix Agent 2;
- Docker/container logging to Loki;
- Greenbone scan/evidence health surfaced in central reporting.

Alloy was updated to 1.20.1 during the 5 October controlled maintenance cycle. Docker-socket access used for container observability is root-equivalent and remains a privileged boundary.

## Backup and protection

VM203 backup target:

```text
storage: media-backup-proxmox-2
job: homelab-nightly-proxmox-2
schedule: 03:15
guests: 101,103,202,203
mode: snapshot
compression: zstd
retention: keep-last=3
```

Current evidence includes:

- manual VM203 snapshot backup and archive-integrity proof;
- unattended VM203 scheduled-backup evidence;
- Proxmox protection enabled.

VM203’s first unattended run is therefore **not** pending.

A representative isolated QEMU restore remains part of the wider recovery-depth backlog.

## IaC ownership

Primary infrastructure path:

```text
IaC/terraform/proxmox/greenbone-01/
```

Greenbone application/scanning/evidence and backup schedule configuration are Git/Ansible managed. Normal orchestration runs from `admin-01`.

## Security boundaries

- administrator credentials remain outside Git;
- scanner targets must be explicitly approved;
- HTTPS remains LAN/VPN-only;
- passive sensor and active scanner responsibilities stay separate;
- Docker socket access is privileged;
- rolling upstream image tags must not be treated as immutable pins;
- raw credentials/evidence secrets must not enter reports or AI prompts.

## 5 October maintenance state

Controlled package maintenance completed with:

- Alloy 1.20.1;
- Docker/container runtime updated and healthy;
- Zabbix Agent 2 updated;
- Greenbone persistent containers healthy;
- `gvmd` healthy;
- no remaining OS updates;
- reboot not required;
- no failed systemd units.

## Remaining follow-up

- maintain feed freshness and monitor disk/resource growth;
- retain scan/evidence/report freshness checks;
- decide whether ICMP timestamp remediation is worth applying through reviewed IaC;
- consider an explicit container-image digest/update policy;
- perform representative QEMU restore proof as part of wider DR work;
- replace self-signed TLS only if it adds operational value.
