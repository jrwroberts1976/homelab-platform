# front-door-camera

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.78` |
| MAC | `3c:52:a1:86:bc:56` |
| DHCP / discovered hostname | `front-door-camera.jameshouse` |
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
- Summary generated: `2026-10-02T00:22:09+01:00`
- MAC identity: `3c:52:a1:86:bc:56`
- Observed IP address(es): `192.168.2.78`
- Connections: **65**
- Traffic sent: **93.6 KiB**
- Traffic received: **82.0 KiB**
- Top services: `dns` (32), `ssl` (20), `dhcp` (2), `ntp` (2)
- Top destination ports: `udp/53` (32), `tcp/443` (20), `udp/1900` (3), `udp/67` (2), `icmp/3` (2), `udp/123` (2)

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
- MAC identity: `3c:52:a1:86:bc:56`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a TP-Link Tapo TC65 camera serving HTTPS and RTSP. TP-Link/Tapo cloud DNS activity and the DHCP hostname support the identity, but the exact firmware or operating system is not established. Nmap produced conflicting legacy Linux/router/camera fingerprints and should not be treated as an exact OS identification.

### Confirmed facts

- The device is online at 192.168.2.78 with hostname front-door-camera.jameshouse.
- Its DHCP hostname is TC65.
- Inventory and Nmap identify the vendor as TP-Link Limited.
- Bounded DNS signals include TP-Link Cloud and Tapo endpoints.
- TCP ports 443/HTTPS and 554/RTSP are open.
- The TLS certificate identifies the device as TPRI-DEVICE.
- Greenbone reported zero matching actionable findings for this IP; this does not prove the device is vulnerability-free or fully assessed.

### Inferences

- The device is likely a TP-Link Tapo TC65 or closely related TP-Link camera model.
- The hostname and RTSP service are consistent with a front-door security camera.
- The device likely uses embedded IoT firmware, possibly Linux-derived, but no precise OS is supported.

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
