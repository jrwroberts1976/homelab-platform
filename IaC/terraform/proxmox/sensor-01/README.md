# sensor-01 Terraform

This stack defines the initial management-side VM for `sensor-01` on `PROXMOX`.

It intentionally creates only the VM system disk, cloud-init and normal management NIC. The future mirrored-port capture adapter is not represented until the physical USB NIC arrives and its stable passthrough identity is known.

## Proposed resources

- node: `PROXMOX`
- VM ID: `201` (must be proved unused)
- management IPv4: `192.168.2.55/24` (must be proved unused)
- 4 vCPU
- 3072 MiB RAM for phase 1 (engines installed but disabled)
- 80 GiB `vm-ssd` disk
- Debian 13
- management NIC on `vmbr0`

## Safety

Run `IaC/ansible/playbooks/proxmox-sensor-prereqs.yml` first so the cloud-init snippet and import storage capability exist.

Before apply, prove:

- VM/CT ID 201 is unused on PROXMOX;
- 192.168.2.55 does not answer ARP/ICMP and is not reserved elsewhere;
- the Terraform plan contains only the Debian image resource and sensor VM;
- no USB/capture device is attached yet;
- PROXMOX retains safe memory headroom after the phase-1 VM starts.

Before Suricata and Zeek are enabled together, perform a second capacity gate.
The current 8 GiB PROXMOX host is not assumed to have enough RAM for the final
dual-engine sensor workload; increase the VM allocation only after host
capacity is addressed and measured.

Persistent Terraform state belongs outside Git under the normal homelab IaC state directory convention.
