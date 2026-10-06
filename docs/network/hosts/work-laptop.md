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
- Summary generated: `2026-10-06T00:24:03+01:00`
- MAC identity: `ec:91:61:9c:a4:45`
- Observed IP address(es): `192.168.2.219`
- Connections: **4,067**
- Traffic sent: **75.1 MiB**
- Traffic received: **1.2 GiB**
- Top services: `ssl` (2395), `dns` (745), `http` (509), `quic` (228), `dhcp` (15), `websocket` (8)
- Top destination ports: `tcp/443` (2416), `udp/53` (601), `tcp/35580` (302), `udp/443` (242), `tcp/80` (160), `udp/5355` (56)

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

- Assessed: `2026-10-01T10:02:06+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `ec:91:61:9c:a4:45`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a work laptop, with DNS activity matching Microsoft Windows Update and delivery endpoints. Exact OS is unconfirmed because Nmap returned no OS or service evidence; manual review is required.

### Confirmed facts

- The observed hostname is work-laptop.jameshouse.
- The DHCP hostname is APL-PF5F6D28.
- The recorded vendor is Cloud Network Technology Singapore PTE.
- DNS observations included Windows Update and Microsoft delivery endpoints.
- Nmap completed only partially and reported missing OS evidence, with no detected TCP or UDP ports.
- No matching actionable Greenbone findings were reported for 192.168.2.219.
- The host was online at the time of the supplied inventory evidence.

### Inferences

- The hostname indicates this is probably a work laptop.
- The Windows Update DNS signal makes a Windows-based endpoint plausible, but does not establish the exact operating system or version.
- The device may use embedded or vendor-specific networking hardware; the supplied evidence does not identify its operating system.

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
