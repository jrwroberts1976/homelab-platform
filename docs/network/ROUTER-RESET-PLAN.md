# Router Clean-Rebuild Plan

**Status:** planned maintenance; not yet executed  
**Router:** ASUS RT-AC86U main router  
**Address:** `192.168.2.1`  
**AiMesh nodes:** `192.168.2.181`, `192.168.2.218`  
**Reviewed:** 12 September 2026

## Goal

Perform a clean firmware/factory-reset rebuild of the router rather than carrying historical configuration drift forward.

The rebuild will deliberately recreate:

- WAN configuration;
- LAN addressing;
- DHCP scope;
- DHCP reservations;
- DNS advertisement;
- Wi-Fi / AiMesh;
- QoS;
- required firewall/port-forward rules;
- DDNS/VPN settings where still required;
- monitoring/syslog integration.

The old configuration is evidence/recovery material only. If the purpose of the reset is to remove historical drift, do **not** blindly restore the old full configuration backup afterward.

## Current network dependencies

Current approved LAN inputs:

```text
router/gateway:  192.168.2.1
primary DNS:     dns-01 / 192.168.2.51
secondary DNS:   dns-02 / 192.168.2.50
IaC controller:  admin-01 / 192.168.2.48
```

`192.168.2.48` is **not** a resolver. It is the administration/IaC controller.

The retired `DietPi` and `TestServer` identities must not appear in the rebuilt DHCP/DNS configuration.

## Relationship with switch repatching

The HP ProCurve physical patching is expected to change when the dedicated `sensor-01` USB capture adapter arrives.

Current switch evidence shows:

- port 24 currently carries the primary ASUS router link;
- port mirroring is disabled;
- port 24 is the planned future SPAN destination.

Before a router clean rebuild, confirm whether the switch repatching has already occurred and use the **then-current** switch map rather than assuming the 12 September snapshot is still physically correct.

The router reset and switch repatch are separate controlled changes. Do not combine them casually into one recovery-ambiguous outage.

## Pre-reset evidence gate

Before any reset:

- export the current router configuration as rollback evidence;
- record firmware version;
- record WAN connection type and ISP-specific requirements;
- record LAN subnet/gateway;
- export/document DHCP reservations;
- record current DHCP lease range;
- record DNS server advertisement;
- record Wi-Fi SSIDs/security mode without committing passwords;
- record AiMesh topology/nodes and their MAC identities;
- record port forwards;
- record VPN server/client configuration;
- record DDNS settings;
- record MAC filtering/access-control rules;
- record QoS state/rules;
- record router syslog/monitoring destination;
- confirm current physical switch port/uplink mapping;
- ensure local wired administration and a recovery route are available.

Secrets, Wi-Fi keys, ISP credentials and private keys must remain in protected secret storage and must never be committed in plaintext.

## Current monitoring/logging dependency

Router syslog currently forwards to:

```text
monitor-01
192.168.2.52
UDP/5514
```

The receiver is operational and writes:

```text
/var/log/homelab/router/rt-ac86u.log
```

A router rebuild must restore that forwarding and revalidate packet/log arrival.

## DHCP direction

The clean rebuild should use a documented reservation plan rather than ad-hoc static addressing.

Every infrastructure reservation should record:

- target hostname;
- MAC address;
- reserved IPv4 address;
- device/role;
- source-of-truth entry in Git.

Current infrastructure identities that must be preserved include the active `.48`, `.50`–`.56`, `.70`, `.71`, `.195`, `.220` and relevant network-device addresses, subject to the final reviewed reservation table.

Do not recreate retired `.242` DNS or the retired `TestServer`/`DietPi` identities.

## DNS cutover safety

Before applying `.51 + .50` as DHCP DNS after a router rebuild, directly validate both resolvers.

At minimum:

```bash
dig @192.168.2.51 example.com A +short
dig @192.168.2.50 example.com A +short
```

Also confirm DNSSEC behaviour and then test a normal client path after DHCP renewal.

A known current IaC parity defect means `dns-02` does not presently return the `dns-01.jameshouse` local record. Treat that as a separate reviewed IaC correction, not a reason to advertise `.48` or another retired resolver.

## QoS direction

QoS should be rebuilt from first principles after the clean reset.

Before defining classes, measure actual WAN upload/download rates and identify traffic that genuinely needs priority. Avoid preserving old rules without evidence.

Likely categories to evaluate:

1. interactive voice/video;
2. DNS and essential infrastructure control traffic;
3. normal client/web traffic;
4. backup/synchronisation;
5. bulk downloads and non-urgent jobs.

The exact ASUS QoS mode and bandwidth values must be decided from the post-reset firmware capabilities and measured WAN performance.

## Cutover safety

A router reset can remove DHCP, DNS advertisement, Wi-Fi and internet access simultaneously.

The reset window must therefore have:

- current config backup available;
- local wired admin access;
- known router recovery procedure;
- both Pi-hole/Unbound services directly checked;
- current switch patching/map available;
- AiMesh rejoin procedure available;
- protected WAN/Wi-Fi/recovery credentials available;
- a written validation checklist.

## Validation after rebuild

Prove:

- router reachable at intended management address;
- WAN/internet works;
- DHCP leases are issued correctly;
- reservations map to intended devices;
- clients receive `192.168.2.51` and `192.168.2.50` as intended DNS;
- both DNS paths resolve successfully;
- Wi-Fi and both AiMesh nodes operate;
- QoS is active only if deliberately configured with measured values;
- required port forwards/VPN/DDNS work;
- syslog forwarding to `.52:5514/udp` is restored;
- monitoring sees the router;
- no retired resolver/host identity was reintroduced;
- physical router-to-switch connectivity matches the current approved port map.

## Change boundary

This document records a future maintenance plan only. Documentation reconciliation does not authorise the router reset, switch repatching, SPAN configuration or DNS IaC changes.
