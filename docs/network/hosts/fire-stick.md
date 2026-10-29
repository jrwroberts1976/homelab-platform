# fire-stick

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.149` |
| MAC | `ac:17:02:07:0d:5d` |
| DHCP / discovered hostname | `fire-stick.jameshouse` |
| MAC vendor | Fibar Group sp. z o.o. |
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

- Zeek flow evidence is not configured for this estate.

> No absence-of-traffic conclusion is made when the Zeek source is unavailable.
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

- Assessed: `2026-10-29T13:02:13+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `ac:17:02:07:0d:5d`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely an Amazon Fire TV-class streaming device, identified by hostname and a 99% Nmap media-device fingerprint. Exact OS/firmware is unsupported. TCP port 8009 is open; no matching actionable Greenbone findings were reported.

### Confirmed facts

- The inventory hostname is fire-stick.jameshouse and the telemetry hostname is fire-stick.
- The Nmap fingerprint reports Amazon Fire TV or Kindle Paperwhite with 99% accuracy and classifies it as an embedded media device.
- TCP port 8009 is open.
- Greenbone completed with zero actionable findings matching 192.168.2.149.
- No authoritative OS fact is available.

### Inferences

- The device is most likely an Amazon Fire TV-class streaming device based on the hostname and Nmap fingerprint.
- The platform is best described cautiously as embedded IoT firmware; the exact OS and firmware version cannot be established from the supplied evidence.
- The inventory-reported vendor is Fibar Group sp. z o.o., which does not corroborate the Amazon device fingerprint.

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
