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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `3c:52:a1:86:bc:56`
- Observed IP address(es): `192.168.2.78`
- Connections: **189**
- Traffic sent: **16.2 MiB**
- Traffic received: **148.1 KiB**
- Top services: `dns` (86), `ssl` (35), `dhcp` (1), `ntp` (1)
- Top destination ports: `udp/53` (86), `tcp/443` (35), `udp/3478` (30), `udp/8089` (8), `tcp/58153` (1), `udp/67` (1)

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
- MAC identity: `3c:52:a1:86:bc:56`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely a TP-Link Tapo network camera, identified by the TC65 DHCP hostname, TP-Link/Tapo cloud DNS activity, vendor data, and camera-oriented estate hostname. Exact firmware/OS is not supported by the evidence.

### Confirmed facts

- The device is online at 192.168.2.78.
- The recorded vendor is TP-Link Limited.
- Its DHCP hostname is TC65 and its inventory hostname is front-door-camera.jameshouse.
- DNS activity includes TP-Link cloud and Tapo endpoints.
- TCP port 443 is open.
- The presented TLS certificate identifies itself as TPRI-DEVICE.
- No actionable Greenbone findings matched this IP in the supplied report; this does not establish that the host is vulnerability-free.

### Inferences

- The device is most likely a TP-Link Tapo camera; TC65 is treated as a model-like hostname rather than a definitively confirmed model.
- The device likely runs embedded IoT firmware.
- The Nmap fingerprint is ambiguous and does not support selecting a precise OS or kernel version.

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
