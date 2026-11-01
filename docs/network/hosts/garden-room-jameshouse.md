# garden-room.jameshouse

<!-- estate-authority: IaC/inventory/estate.json -->

> Automatically created provisional host record from bounded discovery and AI evidence on 2026-10-10. Canonical inventory and direct telemetry remain authoritative.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.74` |
| MAC | `f8:17:2d:65:b8:98` |
| Device / discovered name | garden-room.jameshouse |
| MAC vendor | unknown |
| Stable identity key | MAC |
| Identity confidence | low |

## Profiling and platform evidence

- Device type: unknown network device
- Platform family: unknown
- Exact OS: Not established
- OS confidence: low
- Record state: provisional / automatically created

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `f8:17:2d:65:b8:98`
- Observed IP address(es): `192.168.2.74`
- Connections: **25**
- Traffic sent: **19.8 KiB**
- Traffic received: **17.2 KiB**
- Top services: `ssl` (25)
- Top destination ports: `tcp/443` (25)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->

## Internet / DNS activity

Use bounded service/domain-family summaries here, not raw browsing history. DNS resolution alone does not prove user intent.

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-11-01T16:01:00+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `f8:17:2d:65:b8:98`
- Identity confidence: **low**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Device identity is unresolved. The host is reported as wlan0, but no vendor, OS, service, DNS, or Nmap fingerprint evidence is available. A conflicting DHCP record also reports wlan0 at 192.168.2.74 while the current host IP is 192.168.2.104.

### Confirmed facts

- The current host IP is 192.168.2.104.
- The MAC address is f8:17:2d:65:b8:98.
- The inventory and Nmap hostname is wlan0.
- The device is currently marked online.
- Authoritative OS evidence is unavailable.
- Nmap OS and port evidence is unavailable; the scan status is partial with os_evidence_missing.
- No actionable Greenbone findings match the current IP.
- No sampled Loki warning or error entries were reported.
- A router DHCP record reports hostname wlan0 at 192.168.2.74.

### Inferences

- The hostname wlan0 may represent a wireless-interface-style host name, but it does not establish the device type or operating system.
- The differing IP addresses may reflect stale, historical, or conflicting DHCP/ inventory data and require review.

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
| 2026-10-10 | Provisional host record created automatically for newly assessed MAC | network discovery + AI resolver | pending review |

## Notes

-
