# patio

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.30` |
| MAC | `c4:82:e1:f2:f9:9f` |
| DHCP / discovered hostname | `patio.jameshouse` |
| MAC vendor | Tuya Smart |
| Online at audit | True |
| Stable identity key | MAC |

## Profiling and platform evidence

- Deep-profile status: `baseline`
- Nmap OS evidence: 0 Nmap match(es), needs_os=None
- Observed TCP-port summary: 0 open TCP port(s)
- Automatic device hint: None yet
- Details still to investigate: OS,ports,DNS,device-type

A `baseline` profile means the controlled seven-day backlog has not yet supplied the targeted profile for this device. Zero ports in this summary is therefore not proof that no ports are open.

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-09T00:23:16+01:00`
- MAC identity: `c4:82:e1:f2:f9:9f`
- Observed IP address(es): `192.168.2.30`
- Connections: **67**
- Traffic sent: **52.4 KiB**
- Traffic received: **45.7 KiB**
- Top services: `ssl` (66), `dhcp` (1)
- Top destination ports: `tcp/443` (66), `udp/67` (1)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->

| Direction | Peer / destination | Protocol / port | Purpose | First/last observed | Expected? |
|---|---|---|---|---|---|
| | | | | | |

## Internet / DNS activity

| Signal / service family | Evidence | Interpretation |
|---|---|---|
| No bounded DNS signal recorded yet | automatic dual-Pi-hole evidence | Review with other evidence before identifying the device |

Use service/domain-family summaries here, not raw Pi-hole history. DNS resolution does not prove a person visited a website.

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-08T13:03:48+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `c4:82:e1:f2:f9:9f`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Online Tuya Smart device at 192.168.2.30, identified from inventory and vendor data. No service, DNS, or OS fingerprint evidence is available; exact OS remains unknown.

### Confirmed facts

- The device IP is 192.168.2.30.
- The inventory hostname is patio.jameshouse and the telemetry hostname is patio.
- The reported vendor is Tuya Smart.
- The device is currently online.
- No actionable Greenbone findings match this IP.
- Nmap OS and port data are unavailable; the Nmap profile is partial with os_evidence_missing.
- No sampled Loki entries or recent high-risk DNS policy matches were reported.

### Inferences

- The device is likely a Tuya-based embedded smart-home or IoT device.
- The platform is best described generically as embedded IoT firmware; no precise operating system is supported.
- The DHCP/router hostname wlan0 may be a separate naming signal, but its device meaning is unresolved.

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

## Notes

- 
