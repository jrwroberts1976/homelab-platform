# HP ProCurve Port Map

Status: discovery / target-design working document.

Switch: HP ProCurve 2510G-24  
Legacy management address: `192.168.2.16`

## Port map

Only ports confirmed from live/user evidence are labelled as authoritative. Unknown ports stay `TBD` until cabling is physically traced or the switch MAC/LLDP tables prove the endpoint.

| Port | Current / confirmed use | Target label | State |
|---:|---|---|---|
| 1 | TBD | TBD | DISCOVER |
| 2 | TBD | TBD | DISCOVER |
| 3 | TBD | TBD | DISCOVER |
| 4 | TBD | TBD | DISCOVER |
| 5 | TBD | TBD | DISCOVER |
| 6 | TBD | TBD | DISCOVER |
| 7 | TBD | TBD | DISCOVER |
| 8 | TBD | TBD | DISCOVER |
| 9 | TBD | TBD | DISCOVER |
| 10 | TBD | TBD | DISCOVER |
| 11 | TBD | TBD | DISCOVER |
| 12 | TBD | TBD | DISCOVER |
| 13 | TBD | TBD | DISCOVER |
| 14 | TBD | TBD | DISCOVER |
| 15 | TBD | TBD | DISCOVER |
| 16 | TBD | TBD | DISCOVER |
| 17 | TBD | TBD | DISCOVER |
| 18 | TBD | TBD | DISCOVER |
| 19 | TBD | TBD | DISCOVER |
| 20 | TBD | TBD | DISCOVER |
| 21 | TBD | TBD | DISCOVER |
| 22 | TBD | TBD | DISCOVER |
| 23 | TBD | TBD | DISCOVER |
| **24** | **Mirror/SPAN destination** | **SPAN-DEST -> pve-01 dedicated sensor NIC** | **CONFIRMED** |

## Target physical endpoints requiring switch ports

The following target endpoints need a normal LAN switch port, but no port number is assigned until the existing cabling is traced:

- `pve-01` primary LAN NIC
- `pbs-01` primary LAN NIC
- `dns-01`
- `birdnet-01`
- `media-01`
- ASUS router LAN/uplink connection
- any future dedicated infrastructure endpoint

Port 24 is reserved for mirrored traffic only and is not to carry normal host management/data traffic.

## Mirror/SPAN design

Target path:

```text
selected switch source ports / VLAN traffic
              |
              v
HP ProCurve mirror session
              |
              v
Port 24  [SPAN-DEST]
              |
              v
pve-01 dedicated second NIC
              |
              v
PCI/USB passthrough to sensor-01 VM
              |
              v
Suricata
```

The dedicated capture NIC must have no Proxmox management IP and must not be bridged into the normal LAN.

## Discovery method

Before assigning the remaining port labels:

1. export/record the running switch configuration
2. capture link state for ports 1-24
3. capture MAC address table per port
4. capture VLAN membership
5. capture mirror configuration
6. trace unresolved cables physically
7. update this table in Git
8. apply human-readable switch port names/descriptions where the firmware supports them

No port is to be repatched based only on an assumed hostname.


## Planned factory reset

The switch is now explicitly scheduled for a factory-default rebuild because the current security lock-down prevents practical administration.

The current configuration is not the target source of truth.

Before reset, retain whatever evidence can still be obtained without weakening the device merely for discovery:

- physical cable/port observations
- known management identity
- model/firmware
- any accessible running configuration
- link/MAC/VLAN state if console access exposes it

After reset, rebuild from the documented port map and intended configuration. Port 24 remains reserved as the mirror/SPAN destination throughout the redesign.

The switch rebuild is planned before the ASUS router reset.
