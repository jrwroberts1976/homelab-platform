# Proxmox Guest Backup and Recovery

**Status:** operationally proven primary guest-backup path; scheduled jobs pending  
**Last validated:** 14 September 2026

## Purpose

This runbook documents the current Proxmox VE guest-backup path, validation gates and the proven restore procedure.

The primary guest-backup repository is an NFS export hosted by `media-01` and registered on both standalone Proxmox nodes as `media-backup`.

This is a phase-one backup platform. It does not yet provide an independent secondary copy, and it does not by itself protect non-Proxmox data stored on `media-01`, `docker-01`, the IaC controller, or application-specific consistency requirements such as Nextcloud/PostgreSQL.

## Architecture

```text
PROXMOX .70 ---------\
                      +---- NFS v4.2/TCP ----> media-01 .195
Proxmox-2 .71 -------/                         /srv/backup/pve

PROXMOX .70 ---------\
                      +---- SMTP/25 ----------> mail-relay-01 .54
Proxmox-2 .71 -------/                         -> smtp.gmail.com:587
```

Proxmox storage definition:

```text
nfs: media-backup
        export /srv/backup/pve
        path /mnt/pve/media-backup
        server 192.168.2.195
        content backup
        options vers=4.2,proto=tcp
```

The NFS export permits only the two Proxmox hosts. The backup repository remains root-owned and is not made broadly writable for unprivileged LXC UID mappings.

## Local vzdump workspace

Unprivileged LXC backup to the NFS repository initially failed because the temporary `vzdump` directory on NFS was not writable by the remapped container UID.

The approved design is therefore a local temporary workspace on each hypervisor:

```text
tmpdir: /var/lib/vz/vzdump-tmp
```

Required state:

- owner: `root`;
- group: `root`;
- mode: `1777`;
- minimum deployment gate: 20 GiB free on the filesystem hosting `/var/lib/vz`;
- UID 100000 write test must pass;
- workspace must be empty after validation.

Do not solve the unprivileged-LXC backup problem by making the NFS backup repository broadly writable.

## IaC authority

Relevant playbooks and roles:

```text
IaC/ansible/playbooks/media-backup-target.yml
IaC/ansible/playbooks/proxmox-backup-storage.yml
IaC/ansible/playbooks/proxmox-vzdump-runtime.yml
IaC/ansible/playbooks/proxmox-notification-recipient.yml
IaC/ansible/playbooks/proxmox-mail-relay-client.yml

IaC/ansible/roles/media_backup_target/
IaC/ansible/roles/proxmox_backup_storage/
IaC/ansible/roles/proxmox_vzdump_runtime/
IaC/ansible/roles/proxmox_notification_recipient/
IaC/ansible/roles/proxmox_mail_relay_client/
```

Deployment roles use explicit approval gates. Do not bypass those gates for routine changes.

## Notification path

Both Proxmox nodes use the built-in `mail-to-root` target. `root@pam` is configured with the approved notification recipient.

Both nodes relay outbound mail through:

```text
relayhost = [192.168.2.54]:25
```

`mail-relay-01` is the only host that authenticates to Gmail. The two Proxmox hosts must not send directly to Gmail.

On 14 September 2026 the complete path was proven from both hypervisors:

```text
Proxmox -> mail-relay-01 -> smtp.gmail.com:587 -> recipient
```

Both test messages returned `dsn=2.0.0` and `status=sent`, and the relay queue was empty afterwards.

## Proven backup test

The first successful backup proof used `edge-01`, LXC CT103 on `Proxmox-2`.

Observed result:

```text
backup mode: snapshot
source guest remained running
archive size: approximately 568 MiB
archive compression: zstd
archive integrity: PASS via zstd -t
backup repository: media-backup
local temporary workspace cleaned after backup
```

The tested command shape was:

```bash
vzdump 103 \
  --storage media-backup \
  --mode snapshot \
  --compress zstd
```

Because `/etc/vzdump.conf` now defines the local `tmpdir`, the normal command no longer needs an explicit `--tmpdir` option.

## Proven restore test

On 14 September 2026 the CT103 archive was restored on `Proxmox-2` under temporary VMID `903`.

Safety controls used during the proof:

1. confirmed the source CT103 remained running;
2. confirmed temporary VMID 903 did not already exist;
3. inspected backup metadata/configuration before restore;
4. restored onto `local-lvm` under the temporary VMID;
5. kept the restored container stopped initially;
6. removed every restored network interface before first boot;
7. changed the hostname to an unmistakable restore-test identity;
8. mounted the restored filesystem offline and checked OS/system files;
9. booted the restored container with no production network interface;
10. verified the guest filesystem and OS responded correctly;
11. stopped and destroyed the temporary restore;
12. confirmed the temporary VMID and LVM volume were removed;
13. confirmed live CT103 remained running and the source backup remained present.

Result:

```text
archive_config_gate=PASS
network_isolation=PASS
offline_filesystem_restore=PASS
isolated_boot=PASS
temporary_restore_removed=PASS
restore_proof=PASS
```

This proves the phase-one Proxmox LXC backup path is restorable, not merely writable.

## Manual restore procedure

For a future restore test or recovery:

1. identify the exact backup volume with `pvesm list media-backup`;
2. inspect embedded configuration with `pvesm extractconfig <volid>`;
3. select a proven-unused VMID;
4. restore to suitable local storage while keeping the guest stopped;
5. before any test boot, remove or replace copied production networking to prevent IP/MAC/service conflicts;
6. inspect the restored filesystem offline where possible;
7. boot only after isolation controls are verified;
8. for a test restore, destroy the temporary guest after evidence is collected;
9. for production recovery, deliberately reconcile hostname, network identity, secrets, dependencies and service ownership before returning the restored guest to the LAN.

Never start a cloned restore with the original production IP/MAC configuration while the live source guest is still present.

## Current guest scope

```text
PROXMOX .70
  CT100 dns-02
  CT102 mail-relay-01
  VM200 cloud-01
  VM201 sensor-01

Proxmox-2 .71
  CT101 dns-01
  CT103 edge-01
  VM200 monitor-01
```

Templates are not part of the initial production guest-backup schedule unless explicitly approved.

## Retention

No scheduled backup job is approved until the schedule/retention IaC is deployed and validated.

Initial production retention should be conservative while real estate-wide archive sizes are measured:

```text
keep-last=3
```

After several successful estate-wide runs and capacity review, expand to a deliberate daily/weekly/monthly policy if capacity and recovery objectives support it.

## Validation before enabling schedules

The following are already proven:

- media-01 NFS health and capacity;
- NFS write/read/delete from both hypervisors;
- `media-backup` storage registration on both hypervisors;
- local `vzdump` workspace on both hypervisors;
- successful unprivileged LXC snapshot backup;
- archive integrity test;
- controlled isolated restore and boot;
- Proxmox notification delivery through `mail-relay-01` to Gmail.

Still required before calling the wider backup programme complete:

- scheduled guest backup jobs;
- successful scheduled backup run on both nodes;
- size/capacity review after representative full estate backup;
- VM restore proof in addition to the LXC proof;
- application-consistent recovery proof for `cloud-01`/Nextcloud/PostgreSQL;
- independent secondary copy for important data;
- protection of controller/IaC recovery identities and state;
- protection of non-Proxmox persistent data including `media-01` and `docker-01` where required.

## Failure handling

If a backup fails:

1. do not immediately delete the last known-good backup;
2. verify the source guest is healthy;
3. inspect `vzdump` output and the local temporary workspace;
4. inspect `pvesm status --storage media-backup`;
5. inspect NFS connectivity and `media-01` capacity;
6. confirm `/var/lib/vz/vzdump-tmp` has mode `1777` and sufficient free space;
7. confirm the notification was delivered through `mail-relay-01`;
8. correct the fault through IaC where practical;
9. repeat a manual proof before relying on the next scheduled run if the failure affected the backup path itself.

## Known limitations

- `media-01` is currently the primary guest-backup target, so its own `/srv/media` data is not protected by backing up to itself.
- There is not yet an independent secondary backup copy.
- The suspect 4 TB WD disk on `PROXMOX` must not become the sole trusted copy of important data.
- A successful VM/LXC image backup does not automatically prove application-consistent recovery for databases and stateful applications.
