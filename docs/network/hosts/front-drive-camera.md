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

- Zeek flow evidence is not configured for this estate.

> No absence-of-traffic conclusion is made when the Zeek source is unavailable.
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

- Assessed: `2026-10-01T10:03:30+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `5c:e9:31:18:c1:4a`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a TP-Link Tapo/TC40 network camera. Its hostname, DHCP name, TP-Link/Tapo DNS activity, RTSP service, and HTTPS services support the camera classification, but the exact firmware or operating system is not established.

### Confirmed facts

- The device is identified as front-drive-camera.jameshouse with DHCP hostname TC40.
- The inventory and Nmap data identify the vendor as TP-Link Limited.
- TCP ports 443, 554, and 8443 are open; the services are labeled HTTPS, RTSP, and HTTPS-alt.
- DNS activity includes TP-Link Cloud and Tapo-related endpoints.
- The device has no matching actionable Greenbone findings in the supplied scan data; this does not prove it is vulnerability-free.
- Patch telemetry is unavailable.

### Inferences

- The device is likely a TP-Link Tapo camera, potentially associated with the TC40 model-like DHCP name.
- The platform is most cautiously classified as embedded IoT firmware.
- The Nmap Linux and legacy camera/router fingerprints are tentative and conflicting, so they do not establish an exact operating system.

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
