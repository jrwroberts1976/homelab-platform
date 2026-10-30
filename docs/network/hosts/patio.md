# patio

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.30` |
| MAC | `c4:82:e1:f2:f9:9f` |
| DHCP / discovered hostname | `patio.jameshouse` |
| MAC vendor | Tuya Smart |
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
- MAC identity: `c4:82:e1:f2:f9:9f`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a Tuya Smart embedded IoT device at 192.168.2.109. The hostname is wlan0, but the specific product and operating system are not identified; Nmap returned no OS or port evidence.

### Confirmed facts

- The device is online at 192.168.2.109.
- The recorded hostname and DHCP hostname are wlan0.
- The inventory and Nmap data identify the vendor as Tuya Smart.
- The MAC address is c4:82:e1:f2:f9:9f.
- Nmap status is partial with os_evidence_missing and no reported TCP or UDP ports.
- No matching actionable Greenbone findings were reported for this IP.
- No sampled Loki entries, recent high-risk DNS policy matches, or patch telemetry were reported.

### Inferences

- The device is likely a Tuya Smart embedded IoT product or firmware-based appliance.
- The specific Tuya product model and function cannot be determined from the supplied evidence.
- The operating system or firmware family cannot be determined.

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
