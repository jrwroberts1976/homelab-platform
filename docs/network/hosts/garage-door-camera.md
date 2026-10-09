# garage-door-camera

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.49` |
| MAC | `78:8c:b5:38:16:83` |
| DHCP / discovered hostname | `garage-door-camera.jameshouse` |
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
- Summary generated: `2026-10-09T00:23:16+01:00`
- MAC identity: `78:8c:b5:38:16:83`
- Observed IP address(es): `192.168.2.49`
- Connections: **3,597**
- Traffic sent: **749.1 KiB**
- Traffic received: **753.3 KiB**
- Top services: `dns` (1909), `ssl` (81), `dhcp` (1), `ntp` (1)
- Top destination ports: `udp/53` (1909), `udp/9999` (959), `icmp/3` (646), `tcp/443` (81), `udp/67` (1), `udp/123` (1)

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
- MAC identity: `78:8c:b5:38:16:83`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a TP-Link/Tapo network camera associated with the garage door. The exact model and operating system are not established; Nmap OS results are inconsistent and only one TCP port is confirmed open.

### Confirmed facts

- The device hostname is garage-door-camera.jameshouse.
- The device vendor is identified as TP-Link Limited.
- The DHCP hostname is KC420WS.
- DNS activity includes TP-Link/Tapo-related endpoints such as tplinkcloud.com and api.tplinkra.com.
- TCP port 9999 is open.
- No actionable Greenbone findings match the current IP; this does not prove the host is vulnerability-free.
- Patch telemetry is unavailable.

### Inferences

- The device is likely a TP-Link/Tapo network camera, based on its hostname, vendor, and TP-Link/Tapo DNS signals.
- The platform is best classified cautiously as embedded IoT firmware.
- The DHCP hostname may be model-like, but the supplied evidence does not establish the exact device model.

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
