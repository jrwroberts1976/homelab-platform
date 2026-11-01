# LGwebOSTV

> Automatically created provisional host record from bounded discovery and AI evidence on 2026-10-01. Canonical inventory and direct telemetry remain authoritative.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.130` |
| MAC | `14:7f:67:6d:e5:98` |
| Device / discovered name | LGwebOSTV |
| MAC vendor | LG Innotek |
| Stable identity key | MAC |
| Identity confidence | high |

## Profiling and platform evidence

- Device type: smart TV
- Platform family: embedded IoT firmware
- Exact OS: Not established
- OS confidence: low
- Record state: provisional / automatically created

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `14:7f:67:6d:e5:98`
- Observed IP address(es): `192.168.2.130`
- Connections: **38**
- Traffic sent: **80.3 KiB**
- Traffic received: **181.3 KiB**
- Top services: `ssl` (15), `http` (3), `dns` (1)
- Top destination ports: `tcp/443` (17), `udp/1900` (11), `tcp/80` (3), `udp/56700` (2), `udp/5353` (1), `udp/9999` (1)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->

## Internet / DNS activity

Use bounded service/domain-family summaries here, not raw browsing history. DNS resolution alone does not prove user intent.

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-29T13:02:13+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `14:7f:67:6d:e5:98`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely an LG smart TV identified by its DHCP/inventory hostname and LG Innotek MAC vendor. Exact webOS version or OS is not available; Nmap provided no OS or port evidence.

### Confirmed facts

- The device is online at 192.168.2.130.
- The documented DHCP and inventory hostname is LGwebOSTV.
- The recorded MAC vendor is LG Innotek.
- Authoritative OS information is unavailable.
- Nmap OS and port evidence is unavailable because the profile is partial.
- No actionable Greenbone findings currently match this IP.
- No sampled Loki warning or error entries were reported in the bounded 24-hour sample.

### Inferences

- The hostname strongly suggests the device is an LG webOS television.
- The device likely uses embedded smart-TV firmware, but the exact OS and version are unsupported by the supplied evidence.

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
| 2026-10-01 | Provisional host record created automatically for newly assessed MAC | network discovery + AI resolver | pending review |

## Notes

-
