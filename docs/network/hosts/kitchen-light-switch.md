# kitchen-light-switch

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.167` |
| MAC | `f8:17:2d:64:ca:04` |
| DHCP / discovered hostname | `kitchen-light-switch.jameshouse` |
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

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-26T00:22:36+00:00`
- MAC identity: `f8:17:2d:64:ca:04`
- Observed IP address(es): `192.168.2.167`
- Connections: **69**
- Traffic sent: **54.2 KiB**
- Traffic received: **47.3 KiB**
- Top services: `ssl` (69)
- Top destination ports: `tcp/443` (69)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
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

- Assessed: `2026-10-22T14:00:35+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `f8:17:2d:64:ca:04`
- Identity confidence: **low**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a kitchen light-switch IoT device based on the inventory hostname, but identity is unresolved because the DHCP hostname is wlan0 and no service, vendor, DNS, or Nmap evidence is available.

### Confirmed facts

- The device is online at 192.168.2.167.
- The inventory hostname is kitchen-light-switch.jameshouse and the telemetry hostname is kitchen-light-switch.
- The router reports DHCP hostname wlan0 for 192.168.2.167.
- No Nmap TCP or UDP ports, OS matches, or service evidence are available.
- No MAC vendor, DNS device hint, or canonical estate metadata is available.
- There are no matching actionable Greenbone findings for the current IP; this does not prove the host is vulnerability-free.
- No Loki warning or error samples were recorded in the bounded sample.

### Inferences

- The device may be a kitchen light-switch IoT device.
- An embedded IoT firmware platform is plausible, but unsupported by direct OS evidence.

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
