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
- Summary generated: `2026-10-10T00:20:32+01:00`
- MAC identity: `92:8b:32:14:8b:e9`
- MAC-attributable originated connections: **none observed in this window**

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->

## Internet / DNS activity

Use bounded service/domain-family summaries here, not raw browsing history. DNS resolution alone does not prove user intent.

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-08T11:05:00+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `92:8b:32:14:8b:e9`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Host is identified as an iPhone by its DHCP and telemetry hostname, but no vendor, service, or OS fingerprint evidence is available. Exact OS remains undetermined.

### Confirmed facts

- The DHCP hostname and telemetry hostname are both "iPhone".
- The host used IP address 192.168.2.182 and MAC address 92:8b:32:14:8b:e9.
- The host was reported offline by inventory telemetry.
- Nmap has no recorded TCP or UDP ports or OS matches.
- No actionable Greenbone findings match this IP.
- No locally blocked high-risk DNS policy matches were recorded in the recent one-hour sample.

### Inferences

- The device is likely a mobile device, probably an iPhone, based on the documented hostname.
- The MAC address does not provide a usable vendor identification in the supplied evidence.

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
