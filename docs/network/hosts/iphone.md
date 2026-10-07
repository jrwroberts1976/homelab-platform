# iPhone

> Automatically created provisional host record from bounded discovery and AI evidence on 2026-10-01. Canonical inventory and direct telemetry remain authoritative.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.182` |
| MAC | `92:8b:32:14:8b:e9` |
| Device / discovered name | iPhone |
| MAC vendor | unknown |
| Stable identity key | MAC |
| Identity confidence | medium |

## Profiling and platform evidence

- Device type: smartphone
- Platform family: mobile device firmware
- Exact OS: Not established
- OS confidence: low
- Record state: provisional / automatically created

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-07T00:21:27+01:00`
- MAC identity: `92:8b:32:14:8b:e9`
- MAC-attributable originated connections: **none observed in this window**

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->

## Internet / DNS activity

Use bounded service/domain-family summaries here, not raw browsing history. DNS resolution alone does not prove user intent.

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-01T10:02:06+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `92:8b:32:14:8b:e9`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely an iPhone based on the DHCP and inventory hostname, but vendor and exact operating system are not confirmed. No network services, Nmap OS matches, or vulnerability findings were observed in the supplied evidence.

### Confirmed facts

- The device is identified as "iPhone" by the inventory hostname and telemetry hostname.
- The router reports DHCP hostname "iPhone" for 192.168.2.182.
- The device MAC address is 92:8b:32:14:8b:e9.
- Nmap OS identification is pending with no OS matches or detected ports.
- Greenbone reported zero matching actionable findings for the current IP.
- The router reports the device as online, while inventory reports it as offline.

### Inferences

- The device is likely a smartphone, probably an iPhone, based on the repeated hostname.
- The platform is cautiously classified as mobile device firmware; the exact OS is unsupported by the supplied evidence.
- The MAC address does not provide a reliable vendor identification here.

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
