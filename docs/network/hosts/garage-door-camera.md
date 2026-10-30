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

- Assessed: `2026-10-29T15:01:29+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `78:8c:b5:38:16:83`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely a TP-Link Tapo camera, identified by the camera hostname, TP-Link vendor data, KC420WS DHCP hostname, and Tapo cloud DNS activity. Exact firmware/OS is not established. TCP port 9999 is open without service identification.

### Confirmed facts

- The device is at 192.168.2.49 with MAC address 78:8c:b5:38:16:83.
- The recorded vendor is TP-Link Limited.
- The inventory and Nmap hostname is garage-door-camera.jameshouse.
- The router reports DHCP hostname KC420WS.
- DNS observations include TP-Link/Tapo-related cloud domains, including tplinkcloud.com and tplinkra.com.
- TCP port 9999 is open; no service label is available.
- Nmap reported several Linux/OpenWrt and embedded-device fingerprint matches, but these are fingerprint results rather than an authoritative OS identification.
- No actionable Greenbone findings match the current IP in the supplied scan data.

### Inferences

- The device is most likely a TP-Link Tapo camera, with KC420WS serving as a model-like DHCP hostname.
- The device likely uses embedded Linux-based firmware, but the exact OS, firmware, and version cannot be determined from this evidence.

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
