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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `92:8b:32:14:8b:e9`
- MAC-attributable originated connections: **none observed in this window**

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->

## Internet / DNS activity

Use bounded service/domain-family summaries here, not raw browsing history. DNS resolution alone does not prove user intent.

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-22T13:00:41+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `92:8b:32:14:8b:e9`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Host 192.168.2.182 is identified as an iPhone primarily from consistent DHCP, inventory, router, and Nmap hostnames. No OS, vendor, port, or service evidence is available; the device is currently offline.

### Confirmed facts

- The device IP is 192.168.2.182.
- The DHCP, inventory, router, and Nmap hostnames are all "iPhone".
- The MAC address is 92:8b:32:14:8b:e9.
- Nmap status is pending because fresh ARP presence failed; no ports or OS matches were reported.
- The device is currently marked offline.
- No matching actionable Greenbone findings were reported for this IP.
- No recent high-risk DNS policy matches were reported.
- No Loki entries were sampled for this host in the bounded 24-hour sample.

### Inferences

- The hostname is consistent with an iPhone or another mobile device named "iPhone".
- A mobile platform such as iOS/iPadOS is plausible, but it is not confirmed.
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
