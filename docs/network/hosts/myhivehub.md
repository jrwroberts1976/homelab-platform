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
- Summary generated: `2026-10-09T00:23:16+01:00`
- MAC identity: `00:1c:2b:5a:6d:fd`
- Observed IP address(es): `192.168.2.7`
- Connections: **12,501**
- Traffic sent: **8.4 MiB**
- Traffic received: **33.1 MiB**
- Top services: `ssl` (4220), `dns` (929), `ntp` (48), `dhcp` (1)
- Top destination ports: `tcp/443` (5330), `udp/9953` (4273), `udp/5353` (929), `tcp/853` (170), `udp/123` (48), `udp/67` (1)

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

- Assessed: `2026-10-08T13:03:48+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `00:1c:2b:5a:6d:fd`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Online AlertMe-vendor device identified from its myHiveHub hostname as a likely home automation hub. No exact operating system is supported by the supplied evidence; manual review is required.

### Confirmed facts

- The device is online at 192.168.2.7.
- The recorded hostname is myhivehub.jameshouse, with DHCP hostname myHivehub.
- The reported vendor is Alertme.com Limited.
- The MAC address is 00:1c:2b:5a:6d:fd.
- Nmap status is partial and reports missing OS evidence; no ports or OS matches were supplied.
- No matching actionable Greenbone findings were reported for the current IP.

### Inferences

- The hostname and vendor are consistent with an AlertMe/Hive-style home automation hub.
- The device likely runs embedded IoT firmware, but the specific operating system is unsupported.

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
