# Trusted Firmware-A artifact provenance

## Artifact

- File: `bl31-tfa-2.15.0-release.bin`
- Trusted Firmware-A version: `v2.15.0`
- Platform: Raspberry Pi 4 (`PLAT=rpi4`)
- Build type: release (`DEBUG=0`)
- Upstream repository: `ARM-software/arm-trusted-firmware`
- Original build output: `build/rpi4/release/bl31.bin`

## Build

Build command used during the 2026-10-16 mitigation work:

```text
make realclean
make PLAT=rpi4 DEBUG=0 -j"$(nproc)"
```

## Validated checksum

SHA-256:

```text
b1d31e5094c692b41ee9418a20216176bd1c2764f27e18a5fdc4d6187a307405
```

The resulting release binary was installed on `docker-01` as:

```text
/boot/firmware/bl31-tfa-2.15.0-release.bin
```

The temporary upstream source/build tree was subsequently removed, so a
later byte-for-byte comparison against the original build directory was
not possible.

The installed binary checksum was revalidated before the artifact was
captured into this Ansible role.

## Validated target

- Host: `docker-01`
- Model: Raspberry Pi 4 Model B Rev 1.5
- Revision: `c03115`
- Architecture: `aarch64`
- Operating system: Debian 13

## Boot configuration

```ini
# Trusted Firmware-A for Cortex-A72 speculative execution mitigations
enable_uart=1
enable_gic=1
armstub=bl31-tfa-2.15.0-release.bin
```
