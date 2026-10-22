# rosie-laptop

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.6` |
| MAC | `58:02:05:fd:e1:8b` |
| DHCP / discovered hostname | `rosie-laptop.jameshouse` |
| MAC vendor | Not yet known |
| Online at audit | False |
| Stable identity key | MAC |

## Profiling and platform evidence

- Deep-profile status: `complete`
- Nmap OS evidence: 0 Nmap match(es), needs_os=None
- Observed TCP-port summary: 0 open TCP port(s)
- Automatic device hint: None yet
- Details still to investigate: vendor,OS,ports,device-type

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
| windows_update | automatic dual-Pi-hole evidence | Microsoft/Windows delivery activity observed; supporting clue only |

Use service/domain-family summaries here, not raw Pi-hole history. DNS resolution does not prove a person visited a website.

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-22T14:00:35+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `58:02:05:fd:e1:8b`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a laptop identified as rosie-laptop, with DHCP hostname LAPTOP-SRR7CFCE. DNS telemetry includes Windows Update and Microsoft delivery endpoints, but no authoritative or Nmap OS evidence is available.

### Confirmed facts

- The inventory hostname is rosie-laptop.jameshouse.
- The router reports DHCP hostname LAPTOP-SRR7CFCE for 192.168.2.6.
- The device is associated with MAC address 58:02:05:fd:e1:8b.
- DNS telemetry includes Windows Update and Microsoft delivery endpoint signals.
- No authoritative OS information is available.
- No Nmap ports, services, or OS matches are available.
- No matching actionable Greenbone findings were reported for the current IP.

### Inferences

- The host is likely a laptop based on its documented hostname and DHCP hostname.
- The DNS signals are consistent with a Windows-compatible platform, but do not establish an exact OS or version.

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
