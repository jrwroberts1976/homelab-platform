# work-laptop

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.219` (Wi-Fi), `192.168.2.253` (LAN observed 2026-10-01) |
| Primary MAC (Wi-Fi) | `ec:91:61:9c:a4:45` |
| Alternate MAC (LAN) | `c4:ef:bb:ab:41:66` |
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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `ec:91:61:9c:a4:45`
- Observed IP address(es): `192.168.2.219`
- Connections: **10,696**
- Traffic sent: **1.3 GiB**
- Traffic received: **1.6 GiB**
- Top services: `ssl` (8255), `http` (1388), `quic` (854), `dns` (241), `dhcp` (51), `websocket` (3)
- Top destination ports: `tcp/443` (7269), `tcp/58153` (1069), `udp/443` (885), `tcp/8443` (585), `tcp/80` (300), `udp/5355` (104)

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

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-29T13:02:13+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `ec:91:61:9c:a4:45`
- Identity confidence: **low**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Online client at 192.168.2.113 with DHCP hostname APL-PF5F6D28 and a Cloud Network Technology Singapore PTE. MAC vendor. DNS activity includes Microsoft and Windows Update delivery endpoints, but no ports, service evidence, authoritative OS, or Nmap OS match are available.

### Confirmed facts

- The device is online at 192.168.2.113.
- The DHCP and inventory hostname is APL-PF5F6D28.
- The recorded MAC vendor is Cloud Network Technology Singapore PTE.
- Nmap OS identification is incomplete and returned no OS matches.
- No TCP or UDP ports were reported by Nmap.
- DNS observations included Windows Update and Microsoft delivery endpoints.
- No matching actionable Greenbone findings were reported for the current IP.

### Inferences

- The DNS activity is compatible with a Windows-related client or software component, but it does not establish the device operating system.
- The device identity and device class remain unresolved.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

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
| 2026-10-01 | Confirmed MAC `c4:ef:bb:ab:41:66` / IP `192.168.2.253` is the wired LAN interface of this same machine | new-device detection + user confirmation | James |

## Notes

- 
