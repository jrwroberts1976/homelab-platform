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
- Summary generated: `2026-10-03T00:22:04+01:00`
- MAC identity: `20:23:51:dc:ef:05`
- Observed IP address(es): `192.168.2.29`
- Connections: **739**
- Traffic sent: **722.2 KiB**
- Traffic received: **50.3 KiB**
- Top services: `dns` (9), `ssl` (6), `ntp` (4), `dhcp` (3)
- Top destination ports: `udp/20002` (703), `tcp/443` (16), `udp/53` (9), `udp/123` (4), `udp/67` (3)

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

- Assessed: `2026-10-01T10:04:46+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `20:23:51:dc:ef:05`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a TP-Link Tapo H100 home automation hub at 192.168.2.29. The identity is supported by the documented hostnames, TP-Link vendor data, and TP-Link/Tapo cloud DNS signals. Nmap identifies an embedded lwIP-based network stack, but this does not establish the complete operating system.

### Confirmed facts

- The device is online at 192.168.2.29.
- The documented DHCP/router hostname is H100.
- The inventory hostname is tapo-home-hub-h100.jameshouse.
- The inventory vendor and MAC vendor identify TP-Link PTE.
- DNS activity includes TP-Link/Tapo cloud endpoints.
- TCP port 80 is open.
- Nmap returned lwIP-related OS fingerprints, with the strongest match labeled lwIP 1.4.1–2.0.3.
- Greenbone reported zero actionable findings matching the current IP; this is not proof that the host is vulnerability-free or fully scanned.

### Inferences

- The device is likely a TP-Link Tapo H100 hub based on the H100 hostname, Tapo-style inventory name, TP-Link vendor, and Tapo cloud DNS signals.
- The firmware likely uses the lwIP TCP/IP stack.
- The underlying complete operating system and lwIP version cannot be established from the supplied evidence.

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
