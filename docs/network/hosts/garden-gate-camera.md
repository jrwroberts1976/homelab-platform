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

- Assessed: `2026-10-08T13:03:48+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `3c:64:cf:87:ae:ea`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a TP-Link Tapo network camera, identified from the camera hostname, TC40 DHCP hostname, and repeated TP-Link/Tapo cloud DNS activity. HTTPS and TCP port 554 are open. Exact OS is unsupported; Nmap results are conflicting legacy fingerprints.

### Confirmed facts

- The device is online at 192.168.2.90.
- The documented hostname is garden-gate-camera.jameshouse, with telemetry hostname garden-gate-camera.
- The router reports DHCP hostname TC40.
- DNS activity includes TP-Link cloud and Tapo-related endpoints.
- TCP ports 443 and 554 are open.
- The device presents a TLS certificate with subject and issuer TPRI-DEVICE.
- No matching actionable Greenbone findings were reported for this IP.
- No authoritative OS information is available.

### Inferences

- The device is likely a network camera based on its documented hostname, TC40 model-like DHCP hostname, Tapo-related DNS activity, and the combined network exposure.
- TP-Link/Tapo is the likely vendor or product ecosystem, but the supplied MAC vendor and inventory vendor fields are empty.
- The platform is likely embedded IoT firmware rather than a general-purpose operating system.
- Nmap produced conflicting legacy Linux, router, and webcam fingerprints; these do not establish the exact OS or model.

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
