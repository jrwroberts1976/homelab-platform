# garden-gate-camera

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.90` |
| MAC | `3c:64:cf:87:ae:ea` |
| DHCP / discovered hostname | `garden-gate-camera.jameshouse` |
| MAC vendor | Not yet known |
| Online at audit | True |
| Stable identity key | MAC |

## Profiling and platform evidence

- Deep-profile status: `baseline`
- Nmap OS evidence: 0 Nmap match(es), needs_os=None
- Observed TCP-port summary: 0 open TCP port(s)
- Automatic device hint: None yet
- Details still to investigate: vendor,OS,ports,DNS,device-type

A `baseline` profile means the controlled seven-day backlog has not yet supplied the targeted profile for this device. Zero ports in this summary is therefore not proof that no ports are open.

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-05T00:23:30+01:00`
- MAC identity: `3c:64:cf:87:ae:ea`
- Observed IP address(es): `192.168.2.90`
- Connections: **97**
- Traffic sent: **659.8 KiB**
- Traffic received: **91.7 KiB**
- Top services: `dns` (30), `ssl` (23), `dhcp` (1), `ntp` (1)
- Top destination ports: `udp/49938` (31), `udp/53` (30), `tcp/443` (24), `udp/60458` (3), `udp/3702` (2), `tcp/35580` (1)

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

- Assessed: `2026-10-01T10:07:35+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `3c:64:cf:87:ae:ea`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a TP-Link Tapo TC40 camera at 192.168.2.90. The camera identity is supported by the documented hostname, DHCP hostname, Tapo/TP-Link cloud DNS signals, RTSP service, and device certificate. Exact OS is not established; Nmap returned conflicting legacy Linux, router, and camera fingerprints.

### Confirmed facts

- The device is online at 192.168.2.90.
- Its documented hostname is garden-gate-camera.jameshouse and its DHCP hostname is TC40.
- DNS observations include TP-Link Cloud and Tapo-related endpoints.
- TCP ports 443/HTTPS and 554/RTSP were reported open.
- The TLS certificate identifies itself as TPRI-DEVICE.
- Nmap completed OS detection but returned multiple conflicting fingerprints, including Linux, router, and AXIS network-camera candidates.
- No matching actionable Greenbone findings were reported for this IP; this does not establish that the device is vulnerability-free.
- Patch telemetry is unavailable.

### Inferences

- The device is likely a TP-Link Tapo TC40 camera, based on the DHCP model-like hostname TC40, Tapo DNS signals, camera hostname, and RTSP service.
- It likely runs vendor-specific embedded IoT firmware, possibly Linux-based, but the exact OS and version are unsupported by the evidence.

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
