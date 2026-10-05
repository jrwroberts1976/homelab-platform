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
- Summary generated: `2026-10-05T00:23:30+01:00`
- MAC identity: `14:7f:67:6d:e5:98`
- Observed IP address(es): `192.168.2.130`
- Connections: **49**
- Traffic sent: **108.6 KiB**
- Traffic received: **216.1 KiB**
- Top services: `ssl` (17), `http` (8), `dns` (4), `dhcp` (1)
- Top destination ports: `tcp/443` (19), `udp/1900` (12), `tcp/1990` (5), `udp/5353` (4), `tcp/80` (2), `icmp/3` (2)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->

## Internet / DNS activity

Use bounded service/domain-family summaries here, not raw browsing history. DNS resolution alone does not prove user intent.

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-01T10:02:06+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `14:7f:67:6d:e5:98`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely an LG webOS television based on the documented hostname and LG Innotek vendor attribution. Exact OS/version is not established; Nmap OS identification is incomplete. No matching actionable Greenbone findings were reported, which does not prove the device is vulnerability-free.

### Confirmed facts

- The device is online at 192.168.2.130.
- The documented DHCP, inventory, router, telemetry, and Nmap hostname is LGwebOSTV.
- The recorded vendor is LG Innotek.
- Nmap OS identification is incomplete and reports os_evidence_missing.
- Nmap reported no TCP or UDP ports in the supplied evidence.
- No matching actionable Greenbone findings were reported for this IP.
- Patch telemetry is unavailable.

### Inferences

- The hostname strongly suggests an LG webOS television.
- The device is most appropriately grouped as embedded IoT firmware rather than assigned a specific operating system.

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
