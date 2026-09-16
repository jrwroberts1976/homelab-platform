<!-- estate-authority: IaC/inventory/estate.json -->
# Home Automation / Home Assistant Design

**Status:** planned identity reserved after live collision/capacity preflight; deployment not yet commissioned  
**Reviewed:** 16 September 2026

## Purpose

`home-01` will provide the dedicated home-automation control plane using Home Assistant Operating System (HAOS). The workload is deliberately separated from `docker-01`, which remains the dedicated BirdNET-Go host.

## Approved planned identity

The 16 September live preflight found no collision in repository truth, Proxmox cluster configuration, DNS, ARP/neighbour state or the Network Host Collector for the following reservation:

```text
hostname:     home-01
IPv4:        192.168.2.60/24
VMID:        204
MAC:         02:00:00:00:02:04
Proxmox node: PROXMOX
bridge:       vmbr0
storage:      vm-ssd
```

The identity is recorded as `planned`, not active, until commissioning validation succeeds.

## Deployment model

Use the official Home Assistant OS KVM/Proxmox QCOW2 image rather than Home Assistant Container in an LXC or on `docker-01`.

Pinned initial release:

```text
Home Assistant OS: 18.2
asset: haos_ova-18.2.qcow2.xz
compressed SHA-256: 254e53f354df0739e3afc09be5431a07df53f0df6b703885404f665c454f254e
```

Initial VM resources:

```text
2 vCPU
4096 MiB RAM
32 GiB system disk
OVMF/UEFI firmware
Secure Boot pre-enrolled keys disabled
q35 machine type
VirtIO network
VirtIO SCSI disk
QEMU guest agent enabled
on-boot enabled
```

`PROXMOX` was selected because the live preflight showed materially more available memory and both `local-lvm` and `vm-ssd` active there, while `Proxmox-2` had substantially less available RAM and already hosts the larger monitoring and Greenbone VMs.

## Network commissioning

HAOS uses DHCP by default on first boot. The fixed MAC permits deterministic identification while commissioning.

The approved final address is `192.168.2.60`. Do not publish `home-01` as active or add it to service monitoring until HAOS has been configured to retain that address and both managed DNS resolvers return the intended record.

The management endpoint is expected to become:

```text
http://192.168.2.60:8123
```

No direct WAN exposure is approved. Remote administrative access should use the existing router-hosted VPN unless a later reviewed design chooses another supported Home Assistant remote-access mechanism.

## Radio / device integration

The first build deliberately has no Zigbee, Z-Wave, Thread or Bluetooth USB passthrough.

After the Home Assistant base platform is healthy, choose the radio architecture separately. Prefer a network-attached coordinator where practical if it improves VM mobility and radio placement; if USB passthrough is selected, bind the approved device by stable vendor/product/port identity and document the resulting node-affinity constraint.

## Backup and recovery gates

VM204 is **not** added to the nightly Proxmox backup job during initial creation and Proxmox protection remains disabled.

Commissioning order:

1. create VM204 from the pinned/verified HAOS image;
2. complete initial Home Assistant onboarding;
3. configure and verify the approved `.60` address;
4. create a native Home Assistant backup;
5. configure a network backup destination where appropriate;
6. take and integrity-check a manual Proxmox snapshot backup;
7. perform a recovery validation appropriate to HAOS/native backup state;
8. add VM204 to the node-scoped nightly Proxmox schedule;
9. observe the first unattended backup containing VM204;
10. decide whether to enable Proxmox protection.

Whole-VM backup and native Home Assistant backup are complementary recovery layers; neither should be represented as proof of the other.

## Monitoring

HAOS is an appliance platform and is not an Ansible/Zabbix-Agent2 target by default.

Initial monitoring should use external checks from the existing monitoring platforms, including ICMP/HTTP availability and Home Assistant-specific health only where it is useful and low-noise. Do not expose household entity/state data to monitoring merely to prove platform health.

## IaC ownership

Terraform source lives under:

```text
IaC/terraform/proxmox/home-01/
```

The guarded deployment entry point is:

```text
IaC/scripts/deploy-home-01.sh
```

Terraform state remains outside Git under the controller protected state tree. The deployment script stages the exact pinned HAOS QCOW2 after verifying the upstream compressed SHA-256, requires an explicit deployment gate, accepts only a one-resource VM creation plan, validates the live VM configuration, discovers the first-boot DHCP address through QEMU guest agent and checks Home Assistant HTTP readiness.

## Promotion to active

Promote `home-01` from `planned_assets` to the active estate only after all of the following are true:

- VM204 is running on `PROXMOX` with the approved identity/resources;
- Home Assistant onboarding is complete;
- `192.168.2.60` is persistent and collision-free;
- the UI is reachable on TCP/8123;
- DNS is published and validated on both resolvers;
- native Home Assistant backup exists and its recovery procedure is recorded;
- manual Proxmox backup/integrity proof exists;
- external monitoring is present;
- no unexpected failed platform condition remains.
