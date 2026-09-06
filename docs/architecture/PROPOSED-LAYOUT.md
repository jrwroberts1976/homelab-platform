# Proposed Fresh-Start Homelab Layout

Status: working target design. Final host placement remains subject to completion of the network audit and Proxmox RAM/storage decisions.

```mermaid
flowchart LR
  classDef physical fill:#eef5ff,stroke:#4a78b8,stroke-width:1.5px,color:#12233f
  classDef vm fill:#f6f7f9,stroke:#6d7b8c,stroke-width:1.2px,color:#1b2733
  classDef network fill:#eaf9ef,stroke:#2d9d5b,stroke-width:1.5px,color:#12351f
  classDef peripheral fill:#fff7e8,stroke:#d79a2b,stroke-width:1.2px,color:#49320d

  R["ASUS Router<br/>192.168.2.1<br/>DHCP / QoS / WAN"]:::network
  SW["HP ProCurve 2510G-24<br/>Core switch"]:::network

  R ---|"LAN uplink<br/>port TBD"| SW

  subgraph PHYS["Physical hardware"]
    PVE["pve-01<br/>HP ProDesk<br/>Proxmox"]:::physical
    PBS["pbs-01<br/>ZenBook<br/>Backup server"]:::physical
    DNS1["dns-01<br/>Raspberry Pi 3<br/>Pi-hole + Unbound"]:::physical
    BIRD["birdnet-01<br/>Raspberry Pi 4<br/>BirdNET-Go"]:::physical
    MEDIA["media-01<br/>Raspberry Pi 5<br/>Kodi"]:::physical
    MIC["BirdNET microphone"]:::peripheral
    TV["TV / display"]:::peripheral

    MIC -->|"USB / audio"| BIRD
    MEDIA -->|"HDMI"| TV
  end

  SW ---|"normal LAN<br/>port TBD"| PVE
  SW ---|"normal LAN<br/>port TBD"| PBS
  SW ---|"normal LAN<br/>port TBD"| DNS1
  SW ---|"normal LAN<br/>port TBD"| BIRD
  SW ---|"normal LAN<br/>port TBD"| MEDIA

  subgraph VMS["Virtual services on pve-01"]
    DOCKER["docker-01<br/>containers / applications"]:::vm
    MON["monitoring-01<br/>Prometheus / Grafana / Loki"]:::vm
    MGMT["management-01<br/>Komodo / automation"]:::vm
    SEC["security-01<br/>Greenbone"]:::vm
    SENSOR["sensor-01<br/>Suricata"]:::vm
    DNS2["dns-02<br/>Pi-hole + Unbound"]:::vm
  end

  PVE --> DOCKER
  PVE --> MON
  PVE --> MGMT
  PVE --> SEC
  PVE --> SENSOR
  PVE --> DNS2

  SPAN["Switch port 24<br/>MIRROR / SPAN destination"]:::network
  CAP["Dedicated second NIC on pve-01<br/>no management IP"]:::network

  SW -. "mirrored source traffic" .-> SPAN
  SPAN -->|"physical cable"| CAP
  CAP -->|"direct passthrough"| SENSOR

  SEC -->|"active vulnerability scans"| SW
```

## Confirmed switch-port information

- **Port 24** is the mirror/SPAN destination port.
- Port 24 will connect only to the dedicated capture NIC for `sensor-01`.
- Normal LAN port numbers remain unassigned until the current cabling/MAC table is audited.

See [HP ProCurve Port Map](../network/SWITCH-PORT-MAP.md).

## Router rebuild

The ASUS router will receive a clean firmware/factory-reset rebuild before the final DHCP and QoS configuration is established.

See [Router Clean-Rebuild Plan](../network/ROUTER-RESET-PLAN.md).

## Design intent

- Proxmox hosts the general virtual infrastructure.
- Greenbone runs in `security-01` and scans actively over the normal LAN.
- Suricata runs in `sensor-01` and receives switch-mirrored packets through a dedicated passthrough NIC.
- Kodi remains physical on the Raspberry Pi 5.
- BirdNET-Go remains physical on the Raspberry Pi 4 with the BirdNET microphone attached.
- Primary DNS remains physically independent on the Raspberry Pi 3.
- Backup remains physically independent from Proxmox.
