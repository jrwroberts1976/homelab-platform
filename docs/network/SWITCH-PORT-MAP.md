# HP ProCurve Port Map

**Status:** current-state evidence snapshot plus future repatching intent  
**Switch:** HP ProCurve 2510G-24 / J9279A  
**Management address observed:** `192.168.2.16`  
**Firmware:** Y.11.52  
**Snapshot date:** 12 September 2026

## Purpose

This document separates:

1. **current observed cabling** — evidence captured from live MAC/LLDP/link tables;
2. **future patching intent** — to be designed later when the dedicated sensor USB capture NIC arrives.

The current map must not be treated as the final physical layout.

## Current switch configuration evidence

Read-only console audit confirmed:

- VLAN 1 is the only observed VLAN and ports 1–24 are untagged members;
- management addressing is configured as `dhcp-bootp`;
- STP is disabled;
- port mirroring is disabled;
- SNMP community `public` is configured as `Unrestricted`;
- Telnet management is available;
- SSH management is not available on the current firmware/configuration.

Relevant running configuration:

```text
hostname "ProCurve Switch 2510G-24"
snmp-server community "public" Unrestricted
vlan 1
   name "DEFAULT_VLAN"
   untagged 1-24
   ip address dhcp-bootp
```

These facts are evidence only. Security hardening and switch rebuild decisions belong to a later controlled network change.

## Current evidence-backed port map

| Port | Link state/speed | Current observed endpoint/evidence | Confidence |
|---:|---|---|---|
| 1 | Up / 100FDx | MAC `AC:17:02:07:0D:5D`, ARP neighbour `.149` | MAC/IP proven; device role not documented here |
| 2 | Up / 100FDx | no learned MAC in the captured table | unresolved |
| 3 | Up / 1000FDx | `media-01` `.195`, MAC `2C:CF:67:30:BE:1F` | high |
| 4 | Down | — | unused/down at snapshot |
| 5 | Up / 10FDx | MAC `00:1C:2B:5A:6D:FD`, ARP neighbour `.7` | MAC/IP proven; device role not documented here |
| 6 | Down | — | unused/down at snapshot |
| 7 | Down | — | unused/down at snapshot |
| 8 | Down | — | unused/down at snapshot |
| 9 | Down | — | unused/down at snapshot |
| 10 | Down | — | unused/down at snapshot |
| 11 | Down | — | unused/down at snapshot |
| 12 | Down | — | unused/down at snapshot |
| 13 | Down | — | unused/down at snapshot |
| 14 | Down | — | unused/down at snapshot |
| 15 | Down | — | unused/down at snapshot |
| 16 | Down | — | unused/down at snapshot |
| 17 | Up / 1000FDx | AiMesh node `.181`; LLDP `RT-AC86U`; MAC `04:D4:C4:B8:52:28`; bridged client MACs also learned | high |
| 18 | Up / 1000FDx | `Proxmox-2` `.71`, MAC `00:1A:9F:0C:30:3B`; guest MACs learned behind bridge | very high |
| 19 | Up / 1000FDx | AiMesh node `.218`; LLDP `RT-AC86U`; MAC `04:D4:C4:C1:62:38`; bridged client MACs also learned | high |
| 20 | Up / 1000FDx | `admin-01` `.48`, MAC `B8:27:EB:E8:36:CD` | very high |
| 21 | Up / 1000FDx | `PROXMOX` `.70`, MAC `80:E8:2C:1C:55:D2`; guest MACs learned behind bridge | very high |
| 22 | Down | — | unused/down at snapshot |
| 23 | Up / 1000FDx | `docker-01` wired `.220`, MAC `D8:3A:DD:5A:51:44` | very high |
| **24** | **Up / 1000FDx** | **primary ASUS router `.1`, MAC `24:4B:FE:5E:CC:C8`; LLDP `RT-AC86U`, remote port `eth4`** | **very high** |

## Important port-24 correction

Port 24 is **not currently a SPAN/mirror destination**.

The live command:

```text
show monitor
```

reported:

```text
Port Mirroring is currently disabled.
```

Port 24 currently carries the primary ASUS router connection.

The previous documentation that described port 24 as a confirmed current SPAN destination was incorrect.

## Future repatching intent

The physical patching is expected to change when the new dedicated USB capture adapter arrives.

Agreed intent:

- retain this 12 September table as the pre-repatch evidence snapshot;
- design the final patch layout as a separate task;
- move the current primary-router connection from port 24 to an approved normal LAN/uplink port;
- reserve/repurpose port 24 as the dedicated SPAN destination;
- connect port 24 only to the dedicated capture adapter;
- pass that USB adapter directly to `sensor-01` through `PROXMOX`;
- keep the capture interface free of IP/DHCP/default-route/DNS configuration;
- configure mirroring only as part of the controlled sensor Phase 2 change;
- validate normal LAN connectivity after repatching before activating capture;
- prove mirrored packet arrival with `tcpdump` before enabling Suricata/Zeek.

No cable should be moved purely to make the current table look tidy.

## Future SPAN design

Target path:

```text
selected switch source traffic
              |
              v
HP ProCurve mirror session
              |
              v
Port 24  [future SPAN destination]
              |
              v
dedicated USB Ethernet adapter on PROXMOX .70
              |
              v
USB passthrough to sensor-01 VM
              |
              +--> Suricata
              |
              +--> Zeek
```

## Current MAC evidence used for infrastructure mapping

The 12 September ARP/MAC correlation proved:

```text
192.168.2.1   -> 24:4b:fe:5e:cc:c8 -> switch port 24
192.168.2.70  -> 80:e8:2c:1c:55:d2 -> switch port 21
192.168.2.71  -> 00:1a:9f:0c:30:3b -> switch port 18
192.168.2.181 -> 04:d4:c4:b8:52:28 -> switch port 17
192.168.2.195 -> 2c:cf:67:30:be:1f -> switch port 3
192.168.2.218 -> 04:d4:c4:c1:62:38 -> switch port 19
192.168.2.220 -> d8:3a:dd:5a:51:44 -> switch port 23
```

`admin-01` locally reported Ethernet MAC `b8:27:eb:e8:36:cd`, matching switch port 20.

## Discovery/hardening items for later

Future network work should deliberately review:

- final cable labels and patch layout;
- management address/reservation strategy;
- whether STP should remain disabled;
- removal/replacement of unrestricted SNMP community `public`;
- Telnet-only management limitations;
- final VLAN design if segmentation is introduced;
- switch reset/rebuild decision;
- router reset/rebuild sequencing;
- final SPAN source/destination configuration.

Do not make these changes as part of documentation reconciliation.
