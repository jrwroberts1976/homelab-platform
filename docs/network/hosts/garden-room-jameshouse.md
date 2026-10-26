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
- Summary generated: `2026-10-26T00:22:36+00:00`
- MAC identity: `f8:17:2d:65:b8:98`
- Observed IP address(es): `192.168.2.74`
- Connections: **71**
- Traffic sent: **55.3 KiB**
- Traffic received: **48.4 KiB**
- Top services: `ssl` (70), `dhcp` (1)
- Top destination ports: `tcp/443` (70), `udp/67` (1)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->

## Internet / DNS activity

Use bounded service/domain-family summaries here, not raw browsing history. DNS resolution alone does not prove user intent.

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-25T16:00:11+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `f8:17:2d:65:b8:98`
- Identity confidence: **low**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Online host 192.168.2.74 is identified only by the hostname garden-room.jameshouse and DHCP hostname wlan0. No vendor, service, port, DNS, or OS evidence is available, so the device identity remains unresolved.

### Confirmed facts

- The host is online at 192.168.2.74.
- The inventory hostname is garden-room.jameshouse.
- The router reports DHCP hostname wlan0 for this host.
- The MAC address is f8:17:2d:65:b8:98.
- Nmap completed only partially and reported no TCP or UDP ports or OS matches.
- No authoritative OS, inventory OS, vendor, or kernel data is available.
- No matching actionable Greenbone findings were reported for the current IP; this does not prove the host is vulnerability-free.
- No sampled Loki entries or recent high-risk DNS policy matches were reported.

### Inferences

- The DHCP hostname wlan0 may reflect a wireless interface name, but it does not establish the device type or operating system.

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
