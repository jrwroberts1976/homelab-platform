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
- Summary generated: `2026-10-10T00:20:32+01:00`
- MAC identity: `14:7f:67:6d:e5:98`
- Observed IP address(es): `192.168.2.130`
- Connections: **45**
- Traffic sent: **114.2 KiB**
- Traffic received: **176.3 KiB**
- Top services: `ssl` (15), `dns` (4), `http` (3)
- Top destination ports: `tcp/443` (17), `udp/1900` (13), `udp/5353` (4), `tcp/80` (3), `icmp/3` (2), `udp/56700` (2)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->

## Internet / DNS activity

Use bounded service/domain-family summaries here, not raw browsing history. DNS resolution alone does not prove user intent.

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-08T11:05:00+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `14:7f:67:6d:e5:98`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely an LG webOS smart TV at 192.168.2.130. The hostname and LG Innotek MAC vendor support the identity, but no exact OS evidence or open-service data is available.

### Confirmed facts

- The device hostname is LGwebOSTV.
- The inventory and DHCP hostname are both LGwebOSTV.
- The reported MAC vendor is LG Innotek.
- The device is online at 192.168.2.130.
- Nmap returned no OS matches and no port data.
- No matching actionable Greenbone findings were reported for the current IP.

### Inferences

- The device is likely an LG webOS smart television based on its documented hostname and vendor association.
- The device likely uses embedded IoT firmware, but the exact operating system is unsupported by the supplied evidence.

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
