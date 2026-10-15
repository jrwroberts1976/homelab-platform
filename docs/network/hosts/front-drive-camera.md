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

- Assessed: `2026-10-15T12:02:16+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `5c:e9:31:18:c1:4a`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

TP-Link Tapo/TC40 network camera identified from hostname, DHCP model-like name, vendor, and TP-Link cloud DNS activity. HTTPS is exposed on ports 443 and 8443; port 554 is open. Exact OS or firmware is not established.

### Confirmed facts

- The device hostname is front-drive-camera.jameshouse.
- The DHCP hostname is TC40.
- The inventory vendor and Nmap vendor are TP-Link Limited.
- DNS activity matched TP-Link cloud and Tapo endpoints.
- TCP ports 443 and 8443 provide corroborated HTTPS services.
- TCP port 554 is open; no service label is available for this port.
- No authoritative OS information is available.
- Greenbone reported zero matching actionable findings for this IP; this does not prove the host is vulnerability-free.

### Inferences

- The device is most likely a TP-Link Tapo TC40 network camera used as the front-drive camera.
- The platform is likely embedded IoT firmware.
- Nmap's Linux and network-camera matches are tentative and do not establish an exact OS or firmware version.

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
