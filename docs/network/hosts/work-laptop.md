# work-laptop

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.219` |
| MAC | `ec:91:61:9c:a4:45` |
| DHCP / discovered hostname | `work-laptop.jameshouse` |
| MAC vendor | Cloud Network Technology Singapore PTE. |
| Online at audit | True |
| Stable identity key | MAC |

## Profiling and platform evidence

- Deep-profile status: `partial`
- Nmap OS evidence: 0 Nmap match(es), needs_os=True
- Observed TCP-port summary: 0 open TCP port(s)
- Automatic device hint: None yet
- Details still to investigate: OS,ports,device-type

A `baseline` profile means the controlled seven-day backlog has not yet supplied the targeted profile for this device. Zero ports in this summary is therefore not proof that no ports are open.

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-01T00:23:08+01:00`
- MAC identity: `ec:91:61:9c:a4:45`
- Observed IP address(es): `192.168.2.219`
- Connections: **7,833**
- Traffic sent: **1.3 GiB**
- Traffic received: **3.3 GiB**
- Top services: `ssl` (6266), `quic` (526), `http` (230), `dns` (200), `dhcp` (49), `ssh` (5)
- Top destination ports: `tcp/443` (5808), `udp/443` (555), `tcp/8080` (313), `tcp/8443` (266), `tcp/80` (214), `udp/3478` (203)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->

| Direction | Peer / destination | Protocol / port | Purpose | First/last observed | Expected? |
|---|---|---|---|---|---|
| | | | | | |

## Internet / DNS activity

| Signal / service family | Evidence | Interpretation |
|---|---|---|
| windows_update | automatic dual-Pi-hole evidence | Microsoft/Windows delivery activity observed; supporting clue only |

Use service/domain-family summaries here, not raw Pi-hole history. DNS resolution does not prove a person visited a website.

## Monitoring and security

- Grafana host dashboard:
- Expected services:
- Unexpected services:
- Alerts/findings:
- Firewall/access policy:
- Accepted risks:

## Ownership and administration

- Friendly/reviewed device name:
- Owner / responsible person:
- Physical location:
- Management method:
- Firmware / patching:
- Backup / recovery:
- Planned retirement / replacement:

## Evidence history

| Date | Evidence / change | Source | Reviewed by |
|---|---|---|---|
| 2026-09-29 | Initial persistent host record created from live inventory/detail audit | monitor-01 inventory + deep-profile + DNS state | pending review |

## Notes

- 
