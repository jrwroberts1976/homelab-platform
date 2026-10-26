# acer-lights

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.95` |
| MAC | `60:83:e7:f3:c1:92` |
| DHCP / discovered hostname | `acer-lights.jameshouse` |
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

- Assessed: `2026-10-22T16:05:03+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `60:83:e7:f3:c1:92`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely a TP-Link Tapo P110 smart plug. Identity is supported by the DHCP hostname, TP-Link vendor data, Tapo cloud DNS activity, and the device MAC vendor. Exact firmware/OS is not established; Nmap reported a lwIP stack fingerprint and TCP port 80 open.

### Confirmed facts

- DHCP hostname is P110.
- Inventory and Nmap identify the vendor as TP-Link PTE.
- DNS activity included TP-Link/Tapo cloud endpoints.
- Nmap reported a lwIP 1.4.1–2.0.3 fingerprint; lwIP is a TCP/IP stack rather than a complete OS identification.
- TCP port 80 is open.
- No actionable Greenbone findings matched the current IP; this does not establish that the device is vulnerability-free.

### Inferences

- The device is likely a TP-Link Tapo P110 smart plug, based primarily on the model-like DHCP hostname and Tapo cloud DNS signals.
- The device likely runs embedded IoT firmware, but the exact firmware or operating system is unsupported by the supplied evidence.

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
