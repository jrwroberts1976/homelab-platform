# Clean Debian 13 router SD image build (27 Oct 2026)

Status: IaC **implemented in GitHub, NOT RUN OR BOOT TESTED**. Builds offline *target*, but the builder needs internet to install Debian packages.

## Inputs and security
- Build host is ARM64 Linux `admin-01`, with sudo, loop mounting, xz, free space for decompressed image and apt.
- Use the **official Raspberry Pi OS Lite 64-bit Debian Trixie** `.img.xz` file downloaded from https://www.raspberrypi.com/software/operating-systems/ and verify its published SHA256.
- Base image must use FAT boot partition 1 and ext4 root partition 2.
- Ansible encrypted vault: `/home/james/.config/router-01/pppoe-vault.yml`; provide exact existing username/password **variable names**, not their plaintext values.
- SSH public key: `/home/james/.ssh/id_ed25519.pub`; build provisions user `james` with key-only SSH login and passwordless sudo for Ansible. Protect the private key.
- Output image **contains ISP credentials**. Keep owner-root and mode 0600, do not upload to GitHub or share.

## Build commands from admin-01
```bash
cd ~/projects/homelab-platform
git pull --ff-only origin feature/pi-router-iac-birdnet-poc-migration-20261027
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml playbooks/router-01-image-build.yml --syntax-check
```

Download the current Raspberry Pi OS Lite ARM64 Debian 13 image from the official link above into e.g. `/home/james/router-images/base.img.xz`. Check the SHA256 against the official site. Avoid guessing a release filename.

To identify **only vault variable names** safely, run this locally (no secret values printed):
```bash
ansible-vault view /home/james/.config/router-01/pppoe-vault.yml |
  python3 -c 'import sys,yaml; x=yaml.safe_load(sys.stdin); print("\n".join(sorted(x.keys())))'
```
Requires PyYAML (Ansible normally provides it). Change the two `router_pppoe_*_key` vars below to match the keys shown.

```bash
ansible-playbook -i inventory/hosts.yml playbooks/router-01-image-build.yml \
  --ask-vault-pass --ask-become-pass \
  -e @/home/james/.config/router-01/pppoe-vault.yml \
  -e router_image_base=/home/james/router-images/base.img.xz \
  -e router_image_output=/home/james/router-images/router-01.img \
  -e router_pppoe_username_key=CHANGE_TO_VAULT_USERNAME_KEY \
  -e router_pppoe_password_key=CHANGE_TO_VAULT_PASSWORD_KEY
```

Build creates a *new* disk image and does not touch the running Pi. If the builder fails it can leave an incomplete output .img; remove it only after diagnosing and before rerunning.

## Proposed boot topology
- Pi onboard `eth0`: static `192.168.3.1/24` via systemd-networkd; dnsmasq DHCP `.100-.199`; Unbound DNS at `.3.1`.
- USB Ethernet identified via MAC `00:24:9b:63:b3:8a`, expected name `eth1`; PPPoE uses proved `/etc/ppp/peers/homelab-wan`; NAT via nftables.
- ASUS continues providing `192.168.2.0/24` LAN, with ASUS WAN DHCP on Pi `eth0` (double NAT initially).
- Physical: ONT -> Pi USB WAN; Pi onboard LAN -> ASUS WAN; ASUS LAN -> switch.

## Mandatory before first real cutover
The image builder and the user provisioning flow have NOT been tested. Validate package installation, interface naming, static address, SSH key login, PPPoE credentials, DHCP binding, Unbound and nftables on an isolated setup. Verify the output has the ARM boot files and checksums. Preserve the original SD card; use a spare card if possible. **Do not replace the functioning ASUS routing until the new image is tested.** No automatic cutover/rollback included in this clean-build design. No Suricata installed yet.
