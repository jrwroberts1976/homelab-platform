<!-- estate-authority: IaC/inventory/estate.json -->
# Home Automation / Home Assistant Design

**Status:** commissioned and active; first unattended VM204 backup and external monitoring remain open  
**Reviewed:** 17 September 2026

## Purpose

`home-01` provides the dedicated home-automation control plane using Home Assistant Operating System (HAOS). The workload remains deliberately separated from `docker-01`, which is the dedicated BirdNET-Go host.

## Commissioned identity

The original 16 September live preflight found no collision in repository truth, Proxmox cluster configuration, DNS, ARP/neighbour state or the Network Host Collector. Commissioning on 17 September then validated the following live identity:

```text
hostname:      home-01
IPv4:          192.168.2.60/24
VMID:          204
MAC:           02:00:00:00:02:04
Proxmox node:  PROXMOX
bridge:        vmbr0
storage:       vm-ssd
```

`home-01` is now recorded as an active asset in canonical estate truth.

## Deployment model

The platform uses the official Home Assistant OS KVM/Proxmox image rather than Home Assistant Container in an LXC or on `docker-01`.

Pinned deployed release:

```text
Home Assistant OS: 18.2
asset: haos_ova-18.2.qcow2.xz
compressed SHA-256: 254e53f354df0739e3afc09be5431a07df53f0df6b703885404f665c454f254e
```

Validated VM resources:

```text
2 vCPU
4096 MiB RAM
32 GiB system disk on vm-ssd
OVMF/UEFI firmware
Secure Boot pre-enrolled keys disabled
q35 machine type
VirtIO network
VirtIO SCSI disk
QEMU guest agent enabled
on-boot enabled
Proxmox protection enabled
```

`PROXMOX` remains the selected node. The live VM configuration matches the Terraform design and the QEMU guest agent is functional.

## Home Assistant application state

Validated on 17 September 2026:

```text
Home Assistant Core:       2026.9.2
Supervisor:                2026.09.2
Supervisor healthy:        true
Supervisor supported:      true
Supervisor channel:        stable
Timezone:                  Europe/London
Home Assistant HTTP port:  80
SSL:                       false
```

The live management endpoint is:

```text
http://192.168.2.60/
http://home-01/
```

The HTTP application returned 200 during audit. The unauthenticated `/api/` endpoint returned 401, which is expected and proves the API endpoint is present without disclosing authenticated state.

No direct WAN exposure is approved. Remote administrative access should continue to use the existing router-hosted VPN unless a later reviewed design selects another supported Home Assistant remote-access mechanism.

## Network commissioning

HAOS initially used DHCP during first boot. The fixed MAC provides deterministic identity and the approved production address is now `192.168.2.60`.

Both managed DNS resolvers return:

```text
home-01.jameshouse -> 192.168.2.60
```

Name-based access at `http://home-01/` returned HTTP 200 during the 17 September audit.

## Radio / device integration

The commissioned base VM has no Zigbee, Z-Wave, Thread or Bluetooth USB passthrough.

Radio/device integration remains a separate design decision. Prefer a network-attached coordinator where practical if it improves VM mobility and radio placement; if USB passthrough is selected, bind the approved device by stable vendor/product/port identity and document the resulting node-affinity constraint.

## Backup and recovery

The initial protection and backup gates have now progressed beyond the build state.

Completed evidence:

1. VM204 created from the pinned/verified HAOS image;
2. Home Assistant onboarding completed;
3. approved `.60` address and DNS validated;
4. native Home Assistant backup created;
5. manual Proxmox snapshot backup completed on `media-backup-proxmox`;
6. compressed archive and VMA integrity checks passed;
7. VM204 added to the node-scoped `homelab-nightly-proxmox` 02:15 schedule;
8. Proxmox protection enabled.

Still open:

1. observe the first unattended 02:15 backup containing VM204;
2. decide whether the native Home Assistant backup should also be copied to an independent/off-host destination;
3. perform a deeper recovery validation appropriate to HAOS/native backup state.

Whole-VM backup and native Home Assistant backup are complementary recovery layers; neither should be represented as proof of the other.

## Monitoring

HAOS is an appliance platform and is not an Ansible/Zabbix-Agent2 target by default.

External service monitoring remains an explicit closeout item. Initial monitoring should use low-noise external checks such as ICMP/HTTP availability and Home Assistant-specific health only where useful. Household entity/state data should not be exposed merely to prove platform health.

## IaC ownership

Terraform source lives under:

```text
IaC/terraform/proxmox/home-01/
```

The guarded deployment entry point is:

```text
IaC/scripts/deploy-home-01.sh
```

Terraform state remains outside Git under the controller protected state tree. The deployment workflow verifies the pinned HAOS image, uses explicit safety gates and validates the resulting VM configuration.

The current Terraform desired state includes VM protection and the Home Assistant URL output uses the proven port-80 endpoint.

## Active-state acceptance

`home-01` is now active because the core platform identity and application have been proven live:

- VM204 is running on `PROXMOX` with the approved identity/resources;
- Home Assistant onboarding is complete;
- `192.168.2.60` is live and collision-free;
- the UI is reachable on HTTP port 80;
- DNS is published and validated on both resolvers;
- native Home Assistant backup exists;
- manual Proxmox backup/integrity proof exists;
- VM protection is enabled;
- no unexpected failed platform condition was observed during application audit.

The first unattended VM204 backup, external monitoring and deeper recovery proof remain post-commissioning improvements rather than reasons to continue describing the live service as planned.
