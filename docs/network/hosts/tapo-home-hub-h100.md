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

- Assessed: `2026-10-29T14:02:32+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `20:23:51:dc:ef:05`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

TP-Link H100-class Tapo IoT device identified from hostname, vendor data, and TP-Link/Tapo cloud DNS activity. TCP port 80 is open; Nmap suggests an lwIP-based embedded stack, not a complete operating-system identification. No matching actionable Greenbone findings were reported.

### Confirmed facts

- The device hostname is H100.
- The recorded vendor is TP-Link PTE.
- DNS telemetry includes TP-Link cloud/Tapo endpoints, including security.iot.i.tplinknbu.com and euw1-device-cloudgateway.iot.i.tplinknbu.com.
- TCP port 80 is open.
- Nmap produced lwIP fingerprint matches, including lwIP 1.4.x through 2.x candidates.
- No actionable Greenbone findings match the current IP address 192.168.2.100.
- No authoritative OS fact is available.

### Inferences

- The device is likely a TP-Link Tapo H100-class smart-home hub or related Tapo IoT device.
- The device likely uses embedded firmware with an lwIP TCP/IP stack.

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
