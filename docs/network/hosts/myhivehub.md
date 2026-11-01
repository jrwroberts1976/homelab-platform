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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `00:1c:2b:5a:6d:fd`
- Observed IP address(es): `192.168.2.7`
- Connections: **1,899**
- Traffic sent: **1.8 MiB**
- Traffic received: **4.7 MiB**
- Top services: `dns` (933), `ssl` (923), `ntp` (42)
- Top destination ports: `udp/5353` (933), `tcp/443` (506), `tcp/853` (418), `udp/123` (42)

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

- Assessed: `2026-10-29T15:01:29+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `00:1c:2b:5a:6d:fd`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

myHivehub is an identified AlertMe home-automation hub at 192.168.2.103. The exact firmware or operating system is not available; no open ports or actionable Greenbone findings were reported.

### Confirmed facts

- The device hostname and telemetry hostname are myHivehub.
- The inventory and Nmap vendor are Alertme.com Limited.
- The device is online at 192.168.2.103.
- Nmap is partial and reports no OS matches or ports.
- No actionable Greenbone findings match the current IP.
- No authoritative OS, patch, or service telemetry is available.

### Inferences

- The hostname and Alertme.com Limited vendor strongly indicate a Hive/AlertMe home-automation hub.
- The device likely runs embedded IoT firmware, but the underlying operating system and firmware version are unsupported by the evidence.

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
