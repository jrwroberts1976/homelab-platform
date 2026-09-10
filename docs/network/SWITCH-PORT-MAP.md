# HP ProCurve Port Map

**Status:** current discovery / target-design working document  
**Switch:** HP ProCurve 2510G-24  
**Management address:** `192.168.2.16`  
**Normal controller:** `admin-01.jameshouse` / `192.168.2.48`

## Known switch state

- Model: HP ProCurve 2510G-24 / J9279A.
- Firmware observed: Y.11.52.
- VLAN 1 is the current untagged LAN across the existing design.
- Port 24 is the confirmed mirror/SPAN destination.
- Current management options are constrained; Telnet has historically been available while SSH was not.

Do not invent port assignments where the cable/MAC evidence has not been captured.

## Port map

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
| **24** | **Mirror/SPAN destination** | **SPAN-DEST -> sensor capture path** | **CONFIRMED / RESERVED** |

## Current physical endpoints to account for

Normal LAN ports ultimately need to be identified for the actual physical estate, including:

- ASUS RT-AC86U LAN/uplink connection;
- `PROXMOX` / `192.168.2.70`;
- `Proxmox-2` / `192.168.2.71`;
- `admin-01` / `192.168.2.48` where wired;
- `media-01` / `192.168.2.195`;
- `TestServer` / `192.168.2.220` until it is rebuilt as garden `birdnet-01`;
- any other confirmed wired household endpoints.

The DNS resolvers, `monitor-01`, `cloud-01`, `mail-relay-01`, `sensor-01` and `edge-01` are virtual guests behind the two Proxmox hosts; they do **not** each require separate physical switch ports.

Port 24 is reserved for mirrored traffic and must not carry normal host management/data traffic.

## Mirror/SPAN design

Approved logical target:

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
dedicated capture adapter/path
              |
              v
PROXMOX .70
              |
              v
sensor-01 VM201 / 192.168.2.55 management identity
capture interface with NO IP/DHCP/default route
              |
              +--> Suricata
              |
              +--> Zeek
```

The dedicated capture path is not a Proxmox management interface and must not accidentally become a normal LAN bridge/member.

## Discovery method

Before assigning the remaining port labels:

1. record/export the running switch configuration where possible;
2. capture link state for ports 1-24;
3. capture the MAC-address table per port;
4. capture VLAN membership;
5. capture mirror/SPAN configuration;
6. trace unresolved cables physically;
7. correlate known infrastructure MAC addresses without guessing;
8. update this table in Git;
9. apply human-readable port names/descriptions where firmware supports them.

No cable should be repatched based only on an assumed hostname.

## Planned factory reset

A factory-default rebuild remains planned because the present management baseline is awkward and historical configuration drift is undesirable.

Before reset preserve:

- physical cable/port observations;
- management identity `.16`;
- model/firmware;
- accessible running configuration;
- link/MAC/VLAN state;
- the confirmed port 24 SPAN requirement;
- a local recovery/console path.

After reset, rebuild from documented intent and validate every critical physical endpoint before changing the router.

The switch rebuild should precede a clean ASUS router reset so the wired forwarding layer is known during router cutover.

## Definition of done

The port map is complete when every active wired endpoint is identified by evidence, port 24 remains reserved/proven for the sensor path, VLAN membership is documented, and a future switch rebuild can be performed without relying on undocumented cabling assumptions.
