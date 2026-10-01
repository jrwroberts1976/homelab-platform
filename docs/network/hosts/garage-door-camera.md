# garage-door-camera

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.49` |
| MAC | `78:8c:b5:38:16:83` |
| DHCP / discovered hostname | `garage-door-camera.jameshouse` |
| MAC vendor | TP-Link Limited |
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
- Summary generated: `2026-10-02T00:22:09+01:00`
- MAC identity: `78:8c:b5:38:16:83`
- Observed IP address(es): `192.168.2.49`
- Connections: **2,466**
- Traffic sent: **398.6 KiB**
- Traffic received: **552.5 KiB**
- Top services: `ssl` (70), `ntp` (1)
- Top destination ports: `udp/3478` (1437), `udp/8089` (479), `tcp/443` (70), `udp/28141` (2), `udp/31106` (2), `udp/23268` (2)

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

- Assessed: `2026-10-01T10:06:08+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `78:8c:b5:38:16:83`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a TP-Link Tapo/KC420WS garage-door security camera at 192.168.2.49. TP-Link cloud/Tapo DNS activity and the KC420WS DHCP hostname support the device identity, but the exact operating system is not established.

### Confirmed facts

- The device is online at 192.168.2.49 with MAC address 78:8c:b5:38:16:83.
- Inventory identifies the vendor as TP-Link Limited and the hostname as garage-door-camera.jameshouse.
- The router reports DHCP hostname KC420WS.
- Observed DNS signals include TP-Link/Tapo-related domains such as tplinkcloud.com, api.tplinkra.com, tp-link.com, and stun.tplinkcloud.com.
- Nmap completed and reported TCP port 9999 open with the tentative service name abyss.
- Greenbone reported zero matching actionable findings for this current IP; this is not proof that the host is vulnerability-free or fully scanned.

### Inferences

- The device is likely a TP-Link Tapo KC420WS or closely related TP-Link security camera.
- The platform is best classified broadly as embedded IoT firmware.
- Nmap produced conflicting Linux, OpenWrt, Android, and Philips Hue Bridge fingerprints; these are not sufficient to identify the exact operating system.

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
