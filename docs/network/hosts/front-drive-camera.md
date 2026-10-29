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

- Assessed: `2026-10-22T13:00:41+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `5c:e9:31:18:c1:4a`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely a TP-Link Tapo camera, identified by its hostname, DHCP name TC40, vendor data, and TP-Link cloud/Tapo DNS activity. Exact firmware/OS is not established. HTTPS is available on ports 443 and 8443; port 554 is open. No actionable Greenbone findings matched this IP, which does not prove the host is vulnerability-free.

### Confirmed facts

- Inventory hostname is front-drive-camera.jameshouse and telemetry hostname is front-drive-camera.
- The DHCP hostname and router hostname are TC40.
- Inventory and Nmap vendor data identify TP-Link Limited.
- DNS evidence includes TP-Link cloud and Tapo endpoints.
- Corroborated HTTPS services are exposed on TCP ports 443 and 8443.
- TCP port 554 is open; its Nmap service label was omitted.
- The TLS certificate identifies the device as TPRI-DEVICE.
- No actionable Greenbone findings matched 192.168.2.128.

### Inferences

- The naming, TC40 identifier, TP-Link vendor, and Tapo cloud endpoints strongly indicate a TP-Link Tapo camera.
- The device likely uses embedded IoT firmware, but the exact operating system and firmware version are unknown.
- Generic Nmap matches for Linux, routers, and an AXIS camera are inconsistent and do not establish the device OS or model.

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
