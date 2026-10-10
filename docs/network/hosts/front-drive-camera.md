# front-drive-camera

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.128` |
| MAC | `5c:e9:31:18:c1:4a` |
| DHCP / discovered hostname | `front-drive-camera.jameshouse` |
| MAC vendor | TP-Link Limited |
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
- Summary generated: `2026-10-10T00:20:32+01:00`
- MAC identity: `5c:e9:31:18:c1:4a`
- Observed IP address(es): `192.168.2.128`
- Connections: **548**
- Traffic sent: **1.6 MiB**
- Traffic received: **340.7 KiB**
- Top services: `http` (424), `dns` (30), `ssl` (15), `ntp` (2), `dhcp` (1)
- Top destination ports: `tcp/35580` (425), `udp/60920` (31), `udp/53` (30), `tcp/443` (15), `udp/59759` (15), `udp/49672` (9)

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

- Assessed: `2026-10-08T11:05:00+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `5c:e9:31:18:c1:4a`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely a TP-Link Tapo/TC40 network camera. TP-Link/Tapo DNS activity, the documented camera hostname, vendor data, and HTTPS services support the identity; the exact operating system is not established.

### Confirmed facts

- The device is online at 192.168.2.128.
- The inventory hostname is front-drive-camera.jameshouse and the DHCP hostname is TC40.
- The recorded vendor is TP-Link Limited.
- DNS queries included TP-Link cloud, Tapo, and TP-Link IoT endpoints.
- TCP ports 443, 554, and 8443 were open when scanned.
- Corroborated HTTPS services were reported on TCP ports 443 and 8443.
- No authoritative OS fact is available.
- No matching actionable Greenbone findings were reported for the current IP; this does not establish that the host is vulnerability-free.

### Inferences

- The device is likely a TP-Link Tapo camera, with TC40 possibly identifying the model or device family.
- The platform is consistent with embedded IoT firmware.
- Nmap produced several conflicting legacy Linux, router, and webcam matches; these do not support a precise OS identification.

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
