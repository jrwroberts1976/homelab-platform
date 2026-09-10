# Router Clean-Rebuild Plan

**Status:** planned maintenance; not yet executed  
**Router:** ASUS RT-AC86U / `192.168.2.1`  
**Normal controller:** `admin-01.jameshouse` / `192.168.2.48`  
**Known AiMesh nodes:** `192.168.2.181`, `192.168.2.218`

## Goal

Perform a controlled clean firmware/factory-reset rebuild only when the current configuration, recovery access and post-reset intent are fully documented.

The rebuild should recreate required behaviour from documented intent instead of restoring historical drift wholesale.

## Current critical network facts

```text
LAN:        192.168.2.0/24
Gateway:    192.168.2.1
DNS 1:      192.168.2.51  dns-01
DNS 2:      192.168.2.50  dns-02
Admin:      192.168.2.48  admin-01
PVE:        192.168.2.70, 192.168.2.71
Monitoring: 192.168.2.52  monitor-01
Edge:       192.168.2.56  edge-01
```

`192.168.2.48` is **not** a DNS server. The old DietPi DNS role at `.48` is retired.

## Cloudflare ingress rule

The approved future ingress for selected internal web services is Cloudflare Tunnel through `edge-01` with Cloudflare Access/MFA.

Do not recreate obsolete inbound router port-forwards merely because Nginx Proxy Manager/Authelia once used them. During the pre-reset audit, classify each port-forward as still required, temporary legacy, or removable after Cloudflare cutover.

## Pre-reset evidence gate

Before any reset:

- export the current router configuration as rollback evidence;
- record firmware version and WAN/ISP requirements;
- record LAN subnet/gateway and DHCP lease range;
- export/document DHCP reservations;
- record the current DNS advertisement and verify it is `.51 + .50`;
- record Wi-Fi SSIDs/security mode without exposing passwords;
- record AiMesh topology/nodes;
- record all port forwards and their business/service purpose;
- record VPN/DDNS state still in use;
- record QoS state/rules;
- record access-control/MAC-filtering state where used;
- record router syslog destination `192.168.2.52:5514/udp`;
- prove local wired administration/recovery access;
- keep a tested rollback path available.

Secrets, Wi-Fi keys, ISP credentials and private keys must remain outside Git in protected recovery storage.

## DHCP / reservation direction

DHCP remains on the ASUS router unless a future design change explicitly moves it.

Infrastructure reservations should document:

- hostname;
- MAC address;
- reserved IPv4 address;
- physical/virtual role;
- authoritative Git/IaC/documentation reference.

Preserve current approved fixed identities, including `admin-01 .48` and the core service addresses `.50-.56`, unless a separate migration changes them first.

## DNS advertisement

Post-reset DHCP must advertise exactly the current dual resolver design unless a later reviewed change says otherwise:

```text
192.168.2.51  dns-01
192.168.2.50  dns-02
```

Never restore the historical `.48` or `.242` resolver values.

Before advertising DNS after reset, validate each resolver directly over UDP/TCP and confirm expected `jameshouse` records.

## Router syslog

Restore remote syslog to:

```text
monitor-01 192.168.2.52
UDP port 5514
```

After reset, prove real packets/messages arrive in:

```text
/var/log/homelab/router/rt-ac86u.log
```

Do not modify ASUS SSH `authorized_keys`/`sshd_authkeys` as an incidental part of the router rebuild unless a separate, tested key-migration plan exists.

## QoS direction

Rebuild QoS from measured WAN capacity and actual priority needs rather than preserving old rules by habit.

Evaluate:

1. interactive voice/video;
2. DNS/core infrastructure control traffic;
3. normal client/web traffic;
4. backup/synchronisation;
5. bulk/non-urgent traffic.

## Cutover order

1. ensure the HP ProCurve forwarding layer is stable and locally manageable;
2. capture the router pre-reset evidence;
3. confirm both DNS resolvers and admin-01 are healthy;
4. ensure wired local access to the router is available;
5. reset/reinstall firmware according to ASUS recovery procedure;
6. restore LAN/gateway/DHCP first;
7. restore reservations and `.51 + .50` DNS advertisement;
8. restore Wi-Fi/AiMesh;
9. restore only required VPN/DDNS/port-forward features;
10. restore syslog/monitoring;
11. validate wired and wireless clients before ending the maintenance window.

## Post-reset validation

Prove:

- router reachable at `192.168.2.1`;
- WAN/internet access works;
- DHCP leases are issued correctly;
- infrastructure reservations map to intended devices;
- renewed clients receive `.51 + .50` DNS only;
- both resolvers answer public/local DNS;
- `admin-01 .48` remains administration, not DNS;
- Wi-Fi/AiMesh works;
- required VPN/DDNS functions work;
- required port-forwards only are present;
- no obsolete NPM/Authelia exposure was recreated after Cloudflare cutover;
- router syslog reaches `monitor-01 .52:5514/udp`;
- management SSH access still works using the known authorized path;
- monitoring reports router reachability.

## Definition of done

The clean rebuild is complete only when the documented current network design is restored, clients renew successfully, dual DNS works, Cloudflare-related port-forward decisions are respected, syslog/monitoring are healthy, recovery evidence is stored safely and no obsolete historical configuration has been silently reintroduced.
