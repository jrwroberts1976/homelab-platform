# tapo-home-hub-h100

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.29` |
| MAC | `20:23:51:dc:ef:05` |
| DHCP / discovered hostname | `tapo-home-hub-h100.jameshouse` |
| MAC vendor | TP-Link PTE. |
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

- Assessed: `2026-10-08T13:03:48+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `20:23:51:dc:ef:05`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely TP-Link Tapo H100 home hub at 192.168.2.29. TP-Link/Tapo DNS activity and the H100 hostname support the identity. Nmap reports an lwIP fingerprint and TCP port 80 open, but this does not establish a complete operating system.

### Confirmed facts

- The device is online at 192.168.2.29.
- The inventory hostname is tapo-home-hub-h100.jameshouse and the DHCP hostname is H100.
- The recorded vendor is TP-Link PTE.
- Bounded DNS evidence includes TP-Link cloud and Tapo endpoints.
- TCP port 80 is open.
- Nmap produced lwIP-related fingerprints.
- There are no actionable Greenbone findings matching the current IP in the supplied scan data.

### Inferences

- The device is likely a TP-Link Tapo H100-class smart-home hub.
- The device likely runs embedded IoT firmware using the lwIP TCP/IP stack.
- The exact operating system and firmware version are not established.

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
