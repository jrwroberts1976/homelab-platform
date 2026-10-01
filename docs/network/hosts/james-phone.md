# james-phone

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.206` |
| MAC | `16:c1:05:ad:4b:8a` |
| DHCP / discovered hostname | `james-phone.jameshouse` |
| MAC vendor | Not attributable by OUI (locally administered MAC) |
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
- Summary generated: `2026-10-01T00:23:08+01:00`
- MAC identity: `16:c1:05:ad:4b:8a`
- Observed IP address(es): `192.168.2.206`
- Connections: **9,033**
- Traffic sent: **79.5 MiB**
- Traffic received: **513.7 MiB**
- Top services: `ssl` (6357), `quic` (1646), `dns` (516), `ntp` (141), `http` (72), `dhcp` (5)
- Top destination ports: `tcp/443` (5727), `udp/443` (1722), `udp/5353` (480), `udp/123` (141), `tcp/5228` (91), `tcp/5222` (78)

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

- Assessed: `2026-10-01T10:04:46+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `16:c1:05:ad:4b:8a`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely James's smartphone, based on the documented hostname and DHCP name resembling A13. The exact vendor, model, and operating system are unconfirmed; no scan services or OS fingerprint were obtained.

### Confirmed facts

- The device is online at 192.168.2.206.
- Inventory hostname is james-phone.jameshouse and telemetry hostname is james-phone.
- The DHCP hostname is james-s-A13.
- The MAC address is 16:c1:05:ad:4b:8a.
- Nmap has no recorded TCP or UDP ports or OS matches; its TCP scan reported an error.
- Greenbone has zero actionable findings matching the current IP; this does not prove the device is vulnerability-free.
- No sampled Loki warning or error entries were reported for this host in the bounded 24-hour sample.

### Inferences

- The hostname and DHCP name suggest a smartphone associated with James, possibly an A13-branded/model device.
- The MAC address appears locally administered, so it does not provide a reliable vendor identity.
- The platform is cautiously classified as mobile device firmware; Android or another specific operating system is not established.

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
