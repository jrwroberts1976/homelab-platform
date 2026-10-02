# main-tv

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.234` |
| MAC | `5c:34:00:50:df:b3` |
| DHCP / discovered hostname | `main-tv.jameshouse` |
| MAC vendor | Hisense Electric |
| Online at audit | False |
| Stable identity key | MAC |

## Profiling and platform evidence

- Deep-profile status: `partial`
- Nmap OS evidence: 0 Nmap match(es), needs_os=True
- Observed TCP-port summary: 0 open TCP port(s)
- Automatic device hint: None yet
- Details still to investigate: OS,ports,DNS,device-type

A `baseline` profile means the controlled seven-day backlog has not yet supplied the targeted profile for this device. Zero ports in this summary is therefore not proof that no ports are open.

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-03T00:22:04+01:00`
- MAC identity: `5c:34:00:50:df:b3`
- Observed IP address(es): `192.168.2.234`
- Connections: **3,782**
- Traffic sent: **5.7 MiB**
- Traffic received: **3.0 GiB**
- Top services: `ssl` (456), `http` (63), `dns` (20), `dhcp` (6), `ntp` (6)
- Top destination ports: `udp/1900` (2622), `udp/58747` (527), `tcp/443` (486), `tcp/80` (66), `udp/53521` (37), `udp/53` (20)

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

- Assessed: `2026-10-01T10:03:30+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `5c:34:00:50:df:b3`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a Hisense smart TV using embedded IoT firmware. The hostname and vendor data support the identity, while Nmap found no OS evidence or exposed services. Vidaa and Netflix-related DNS activity is consistent with TV use but does not establish an exact OS.

### Confirmed facts

- The documented hostname is main-tv.jameshouse, with telemetry hostname main-tv.
- The inventory vendor is Hisense Electric.
- The MAC address is 5c:34:00:50:df:b3.
- The device has IP address 192.168.2.234.
- Nmap status is partial and reports os_evidence_missing; no TCP or UDP ports were recorded.
- The DNS sample includes Vidaa-related domains, YouTube, and Netflix domains.
- No matching actionable Greenbone findings were reported for this IP.
- Patch telemetry is unavailable.

### Inferences

- The device is likely a Hisense smart TV based on its hostname, vendor, and Vidaa-related DNS activity.
- The platform is likely embedded IoT firmware, but the exact operating system is unsupported by the supplied evidence.
- The Vidaa and streaming-related DNS activity is consistent with smart-TV usage, but does not prove a specific firmware or OS.

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
