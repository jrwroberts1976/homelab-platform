# tapo-home-hub-h100

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.29` |
| MAC | `20:23:51:dc:ef:05` |
| DHCP / discovered hostname | `tapo-home-hub-h100.jameshouse` |
| MAC vendor | TP-Link PTE. |
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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `20:23:51:dc:ef:05`
- Observed IP address(es): `192.168.2.29`
- Connections: **705**
- Traffic sent: **609.0 KiB**
- Traffic received: **5.0 KiB**
- Top services: `ntp` (4), `dhcp` (1), `ssl` (1)
- Top destination ports: `udp/20002` (699), `udp/123` (4), `udp/67` (1), `tcp/443` (1)

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

- Assessed: `2026-10-22T15:00:05+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `20:23:51:dc:ef:05`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Identified as a TP-Link Tapo H100 smart-home hub from the documented hostname, vendor data, DHCP hostname, and TP-Link/Tapo cloud DNS activity. The exact firmware OS is not supported by the evidence; Nmap only provides a tentative lwIP TCP/IP stack fingerprint. TCP port 80 is open. No actionable Greenbone findings matched the current IP.

### Confirmed facts

- The inventory hostname is tapo-home-hub-h100.jameshouse and the telemetry hostname is tapo-home-hub-h100.
- The router reports DHCP hostname H100 for 192.168.2.29.
- The inventory vendor is TP-Link PTE.
- DNS activity includes TP-Link cloud/Tapo endpoints.
- TCP port 80 is open.
- Greenbone reported zero matching actionable findings for the current IP.

### Inferences

- The device is most likely a TP-Link Tapo H100 smart-home hub.
- The platform is likely embedded IoT firmware.
- The Nmap fingerprint suggests an lwIP-based TCP/IP stack, but lwIP is not treated as the device operating system.

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
