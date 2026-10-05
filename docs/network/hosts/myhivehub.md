# myhivehub

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.7` |
| MAC | `00:1c:2b:5a:6d:fd` |
| DHCP / discovered hostname | `myhivehub.jameshouse` |
| MAC vendor | Alertme.com Limited |
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

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-05T00:23:30+01:00`
- MAC identity: `00:1c:2b:5a:6d:fd`
- Observed IP address(es): `192.168.2.7`
- Connections: **9,640**
- Traffic sent: **6.6 MiB**
- Traffic received: **25.0 MiB**
- Top services: `ssl` (5679), `dns` (921), `ntp` (43), `dhcp` (1)
- Top destination ports: `tcp/443` (5681), `udp/5353` (921), `udp/123` (43), `udp/67` (1)

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

- Assessed: `2026-10-01T10:06:08+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `00:1c:2b:5a:6d:fd`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely an AlertMe-associated home automation hub based on its hostname and vendor. Exact operating system and service profile are unavailable; manual review is required.

### Confirmed facts

- The device is online at 192.168.2.7.
- The recorded hostname is myhivehub.jameshouse, with DHCP hostname myHivehub.
- The inventory vendor and Nmap vendor are Alertme.com Limited.
- The MAC address is 00:1c:2b:5a:6d:fd.
- Nmap OS and port evidence is unavailable because the scan is partial and reports os_evidence_missing.
- No actionable Greenbone findings currently match this IP.
- Patch telemetry is unavailable.

### Inferences

- The hostname and AlertMe vendor are consistent with a home automation hub.
- The device likely uses embedded IoT firmware, but the specific operating system is unsupported by the supplied evidence.

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
