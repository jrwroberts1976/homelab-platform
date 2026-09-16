<!-- estate-authority: IaC/inventory/estate.json -->
# Homelab Greenbone Vulnerability Scanner Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** operational; commissioned and protected; LAN-only  
**Host:** `greenbone-01.jameshouse`  
**IPv4:** `192.168.2.57`  
**Placement:** VM 203 on `Proxmox-2` / `192.168.2.71`  
**Last current-state review:** 16 September 2026

## Purpose

`greenbone-01` provides active vulnerability scanning for the homelab.

It complements rather than replaces `sensor-01`:

- `sensor-01` performs passive Suricata/Zeek observation;
- `greenbone-01` actively probes approved targets;
- neither service depends directly on the other.

## Platform

Validated VM state:

```text
VMID:       203
name:       greenbone-01
node:       Proxmox-2
IPv4:       192.168.2.57
vCPU:       4
RAM:        8192 MiB
disk:       80 GiB local-lvm
protection: enabled
```

The guest runs Debian 13 and the Greenbone Community Container stack through Docker Compose.

The Community Container deployment is appropriate for this homelab scanner, but it must not be documented as an immutable appliance or as a general production-support commitment. Upstream rolling image tags can change between pulls.

## Exposure

The approved exposure is LAN-only:

```text
192.168.2.57:443  Greenbone HTTPS
127.0.0.1:443     internal nginx binding
127.0.0.1:9392    internal Greenbone service path
```

There is no approved public or Cloudflare exposure.

The current HTTPS certificate is self-signed.

## Feed readiness

Commissioning completed only after all required feed families reported ready:

```text
openvas_vt_cache=READY
gvmd_vts=READY
scap=READY
cert=READY
feed_ready=4/4
```

Commissioning evidence also recorded:

```text
OpenVAS VT feed version: 202609140600
VT count:                 187151
Full and fast config:     available
```

## Commissioning scan

A controlled self-scan of `192.168.2.57` completed successfully.

```text
Critical: 0
High:     0
Medium:   0
Low:      1
Log:      9
```

The single Low result was:

```text
ICMP Timestamp Reply Information Disclosure
severity: 2.1
```

That item is accepted for scanner commissioning and remains a separate IaC-managed hardening follow-up. Do not apply an undocumented ad-hoc firewall rule merely to suppress the finding.

The remaining nine results were informational/log observations such as service and header enumeration.

## Monitoring and logging

Current host observability includes:

- Node Exporter;
- Alloy 1.19.2;
- Docker container log collection;
- proven ingestion of Greenbone logs into Loki;
- host/service health validation.

Alloy requires Docker socket access for the deployed log-discovery design. Docker socket access is effectively root-equivalent privilege and must be treated accordingly.

## Backup and protection

VM203 has independent backup proof on:

```text
media-backup-proxmox-2
```

Two manual snapshot archives were present during final commissioning, and archive integrity was proven using `zstd -t`.

The IaC-managed `Proxmox-2` nightly job is:

```text
job:       homelab-nightly-proxmox-2
schedule:  03:15
storage:   media-backup-proxmox-2
guests:    101,103,202,203
mode:      snapshot
compress:  zstd
retention: keep-last=3
```

The reconciliation that added VM203 completed successfully and a second run was idempotent with `changed=0`.

VM203 Proxmox protection is enabled. Terraform converged with no remaining changes after protection was applied.

The temporary `pre-greenbone-stack` commissioning snapshot was removed only after the independent backup and protection gates passed.

The first unattended 03:15 cycle including VM203 remains to be observed.

## IaC ownership

Primary Terraform path:

```text
IaC/terraform/proxmox/greenbone-01/
```

Relevant Ansible includes the Greenbone baseline/application roles and the central Proxmox backup-schedule role.

Normal controller:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

Terraform is the approved VM provisioning tool for this deployment.

## Security decisions

- Greenbone administrator credentials are not stored in Git.
- Default administrator credentials were replaced during commissioning.
- Future deployment sequencing should rotate the default administrator credential before enabling the LAN listener.
- HTTPS remains LAN-only.
- Scanner targets must be deliberately approved.
- Do not merge passive sensor and active scanner responsibilities.
- Do not expose the Docker socket beyond the local observability requirement.
- Do not assume rolling container tags provide image immutability.

## Remaining follow-up

- observe the first unattended VM203 scheduled backup;
- manage the ICMP timestamp response through approved IaC if remediation is desired;
- perform a representative isolated QEMU restore proof;
- consider explicit container-image digest/update policy;
- replace self-signed TLS only if operationally useful;
- continue monitoring feed freshness, disk use and scanner resource impact.
