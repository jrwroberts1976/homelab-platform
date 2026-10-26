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
- Summary generated: `2026-10-26T00:22:36+00:00`
- MAC identity: `3c:64:cf:87:ae:ea`
- Observed IP address(es): `192.168.2.90`
- Connections: **355**
- Traffic sent: **30.1 MiB**
- Traffic received: **1.5 MiB**
- Top services: `dns` (102), `ssl` (48), `quic` (5), `dhcp` (1), `ntp` (1)
- Top destination ports: `udp/53` (102), `udp/3478` (67), `tcp/443` (44), `udp/8089` (11), `udp/443` (5), `udp/57040` (2)

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
- MAC identity: `3c:64:cf:87:ae:ea`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a TP-Link Tapo camera, identified by its camera hostname, DHCP name TC40, and TP-Link/Tapo cloud DNS activity. Exact firmware or operating system is not established.

### Confirmed facts

- The device hostname is garden-gate-camera.jameshouse.
- The DHCP hostname is TC40.
- The device is online at 192.168.2.90.
- TCP port 443 is open.
- TLS on port 443 presents a certificate with subject and issuer TPRI-DEVICE.
- DNS observations include TP-Link cloud and Tapo endpoints.
- No matching actionable Greenbone findings were reported for this IP; this does not prove the host is vulnerability-free.

### Inferences

- The device is likely a TP-Link Tapo camera based on its hostname and TP-Link/Tapo DNS signals.
- The device likely runs embedded IoT firmware.
- The Nmap OS results are ambiguous and include generic Linux, router, and camera fingerprints; they do not establish the exact device model or operating system.

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
