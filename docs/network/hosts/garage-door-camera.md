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

- Assessed: `2026-10-22T15:00:05+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `78:8c:b5:38:16:83`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

TP-Link smart camera, likely model KC420WS, identified from estate naming, DHCP hostname, vendor data, and TP-Link/Tapo DNS activity. Exact firmware/OS is not supported by the evidence. TCP port 9999 is open; no matching actionable Greenbone findings were reported.

### Confirmed facts

- The device is online at 192.168.2.49.
- The documented inventory hostname is garage-door-camera.jameshouse, with telemetry hostname garage-door-camera.
- The recorded vendor is TP-Link Limited.
- The DHCP hostname is KC420WS.
- DNS telemetry includes TP-Link cloud, Tapo, and tplinkra.com endpoints.
- TCP port 9999 is open.
- Greenbone reported zero matching actionable findings for the current IP.

### Inferences

- The device is a TP-Link smart security camera associated with a garage-door monitoring role.
- KC420WS is likely a model-like identifier for the device.
- The device likely uses embedded IoT firmware, but the exact OS and firmware version cannot be established.
- Nmap produced Linux/OpenWrt-oriented and other embedded-device candidates, but these are not sufficient to identify the exact OS.

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
