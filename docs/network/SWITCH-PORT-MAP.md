<!-- estate-authority: IaC/inventory/estate.json -->
# HP ProCurve Port Map

**Status:** HISTORICAL 12 SEPTEMBER CABLING SNAPSHOT — CURRENT SPAN STATE SUPERSEDES PORT 24 ENTRY  
**Switch:** HP ProCurve 2510G-24 / J9279A  
**Management address:** `192.168.2.16`  
**Firmware:** Y.11.52  
**Snapshot date:** 12 September 2026  
**Current-state review:** 6 October 2026

## Read this first

The table below is retained as **dated physical evidence from 12 September**. It is not the current cabling authority after the sensor/SPAN repatch.

Current validated switch monitoring state is:

```text
mirror destination: port 24
mirror sources:     ports 1-23
```

`sensor-01` is actively receiving mirrored traffic through the dedicated capture path. Therefore the old row that shows the ASUS router on port 24 and the old statement that mirroring was disabled are historical observations only.

A fresh port-by-port physical mapping remains required if current cable placement matters operationally. Do not invent which normal switch port now carries the router uplink without new evidence.

## 12 September switch configuration snapshot

At the snapshot date, read-only console evidence showed:

- VLAN 1 untagged on ports 1–24;
- management address via `dhcp-bootp`;
- STP disabled;
- mirroring disabled at that time;
- SNMP community `public` configured `Unrestricted`;
- Telnet management available;
- SSH management unavailable on the observed firmware/configuration.

Historical running configuration excerpt:

```text
hostname "ProCurve Switch 2510G-24"
snmp-server community "public" Unrestricted
vlan 1
   name "DEFAULT_VLAN"
   untagged 1-24
   ip address dhcp-bootp
```

## Historical evidence-backed port map — 12 September 2026

| Port | Link state/speed | Observed endpoint/evidence at snapshot | Confidence |
|---:|---|---|---|
| 1 | Up / 100FDx | MAC `AC:17:02:07:0D:5D`, ARP `.149` | MAC/IP proven |
| 2 | Up / 100FDx | no learned MAC in captured table | unresolved |
| 3 | Up / 1000FDx | `media-01` `.195`, MAC `2C:CF:67:30:BE:1F` | high |
| 4 | Down | — | snapshot only |
| 5 | Up / 10FDx | MAC `00:1C:2B:5A:6D:FD`, ARP `.7` | MAC/IP proven |
| 6–16 | mostly down | see original 12 September evidence | snapshot only |
| 17 | Up / 1000FDx | AiMesh `.181`, MAC `04:D4:C4:B8:52:28` | high |
| 18 | Up / 1000FDx | `Proxmox-2` `.71`, MAC `00:1A:9F:0C:30:3B` | very high |
| 19 | Up / 1000FDx | AiMesh `.218`, MAC `04:D4:C4:C1:62:38` | high |
| 20 | Up / 1000FDx | `admin-01` `.48`, MAC `B8:27:EB:E8:36:CD` | very high |
| 21 | Up / 1000FDx | `PROXMOX` `.70`, MAC `80:E8:2C:1C:55:D2` | very high |
| 22 | Down | — | snapshot only |
| 23 | Up / 1000FDx | `docker-01` `.220`, MAC `D8:3A:DD:5A:51:44` | very high |
| 24 | Up / 1000FDx | ASUS router `.1`, MAC `24:4B:FE:5E:CC:C8` | **historical — superseded by current SPAN destination** |

This table must not be used to infer current physical cabling after the repatch.

## Current SPAN architecture

```text
switch ports 1-23
      |
      | monitored sources
      v
HP ProCurve mirror session
      |
      v
port 24 — mirror destination
      |
      v
dedicated USB Ethernet capture adapter
      |
      v
PROXMOX USB passthrough
      |
      v
sensor-01
  +-- Suricata
  +-- Zeek
```

The capture interface carries no normal management role and must remain isolated from management/Corosync routing.

## Current known switch constraints

- legacy Telnet-only management path;
- unrestricted `public` SNMP community remains a hardening concern/risk-accepted item unless separately changed;
- VLAN 1 remains the documented untagged baseline;
- physical cable labels/port assignments require a fresh audit after repatching;
- SPAN must remain operational when any cabling or switch configuration is changed.

## Next physical-network documentation action

When physical access is convenient, perform a new read-only MAC/LLDP/link/console audit and create a **new dated current map**. Do not rewrite this snapshot; preserving the pre-repatch map is useful historical evidence.
