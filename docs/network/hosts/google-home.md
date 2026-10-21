# google-home

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.17` |
| MAC | `a4:77:33:5f:94:fe` |
| DHCP / discovered hostname | `google-home.jameshouse` |
| MAC vendor | Google |
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
- Summary generated: `2026-10-21T00:24:48+01:00`
- MAC identity: `a4:77:33:5f:94:fe`
- Observed IP address(es): `192.168.2.17`
- Connections: **6,920**
- Traffic sent: **10.8 MiB**
- Traffic received: **8.1 MiB**
- Top services: `dns` (3658), `ssl` (885), `quic` (424), `ntp` (91), `http` (28), `dhcp` (2)
- Top destination ports: `udp/53` (2430), `udp/5353` (1228), `udp/9478` (1098), `udp/9999` (938), `tcp/443` (607), `udp/443` (431)

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

- Assessed: `2026-10-15T13:01:53+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `a4:77:33:5f:94:fe`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Google Home device at 192.168.2.17, identified by its DHCP/inventory hostname, Google vendor data, Nmap fingerprint, and Chromecast-related Google TLS certificate. Exact OS is not established.

### Confirmed facts

- The device IP is 192.168.2.17 and its MAC address is a4:77:33:5f:94:fe.
- The documented DHCP and inventory hostnames are Google-Home and google-home.jameshouse.
- Inventory and Nmap identify the vendor as Google.
- Nmap's top fingerprint is Google Home device with 99% accuracy and media-device classification.
- TCP ports 8008, 8009, and 8443 are open; Nmap labels for these ports were omitted.
- TCP ports 8443 and 9000 have corroborated HTTPS-alt and cslistener service records, respectively.
- The TLS certificate on port 8443 is issued by Chromecast ICA 6 (Audio Assist) and identifies Google Inc.
- No actionable Greenbone findings matched the current host IP in the supplied scan.

### Inferences

- The host is most likely a Google Home/Chromecast-family embedded media or smart-speaker device.
- The exact operating system or firmware is not supported by the supplied evidence; Nmap Linux matches are treated as tentative platform fingerprints rather than an exact OS identification.

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
