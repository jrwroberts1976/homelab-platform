# james-lt

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.183` |
| MAC | `24:b2:b9:30:f8:55` |
| DHCP / discovered hostname | `james-lt.jameshouse` |
| MAC vendor | Not yet known |
| Online at audit | True |
| Stable identity key | MAC |

## Profiling and platform evidence

- Deep-profile status: `baseline`
- Nmap OS evidence: 0 Nmap match(es), needs_os=None
- Observed TCP-port summary: 0 open TCP port(s)
- Automatic device hint: None yet
- Details still to investigate: vendor,OS,ports,DNS,device-type

A `baseline` profile means the controlled seven-day backlog has not yet supplied the targeted profile for this device. Zero ports in this summary is therefore not proof that no ports are open.

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-03T00:22:04+01:00`
- MAC identity: `24:b2:b9:30:f8:55`
- Observed IP address(es): `192.168.2.183`
- Connections: **10,648**
- Traffic sent: **917.9 MiB**
- Traffic received: **9.5 GiB**
- Top services: `ssl` (4075), `http` (2810), `dns` (1922), `quic` (1215), `smb` (3), `gssapi` (2)
- Top destination ports: `tcp/443` (3881), `tcp/80` (2225), `udp/443` (1238), `udp/53` (1225), `udp/5353` (579), `tcp/38400` (553)

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

- Assessed: `2026-10-01T10:03:30+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `24:b2:b9:30:f8:55`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Online endpoint at 192.168.2.183 identified by DHCP and inventory hostname as James-LT. Its laptop-like role is inferred from the hostname; no OS, vendor, service, or Nmap fingerprint evidence is available.

### Confirmed facts

- The current IP is 192.168.2.183.
- The device is online according to inventory and router data.
- The documented inventory hostname is james-lt.jameshouse, with telemetry hostname james-lt.
- The DHCP hostname is James-LT.
- The MAC address is 24:b2:b9:30:f8:55.
- Nmap OS and port evidence is unavailable; the scan status is partial with os_evidence_missing.
- No enriched services, Zeek connections, or top ports/services were reported.
- Greenbone reported zero matching actionable findings for the current IP; this is not proof that the host is vulnerability-free or fully scanned.
- Patch telemetry is unavailable.
- No sampled Loki entries or warning/error samples were reported for the bounded 24-hour sample.

### Inferences

- The hostname convention suggests a laptop-like endpoint.
- The operating system and hardware vendor cannot be determined from the supplied evidence.

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
