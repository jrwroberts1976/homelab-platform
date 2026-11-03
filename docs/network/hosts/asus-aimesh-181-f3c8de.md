# asus-aimesh-181

> Automatically created provisional host record from bounded discovery and AI evidence on 2026-11-03. Canonical inventory and direct telemetry remain authoritative.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.181` |
| MAC | `60:83:e7:f3:c8:de` |
| Device / discovered name | asus-aimesh-181 |
| MAC vendor | TP-Link PTE. |
| Stable identity key | MAC |
| Identity confidence | low |

## Profiling and platform evidence

- Device type: network device
- Platform family: embedded IoT firmware
- Exact OS: Not established
- OS confidence: low
- Record state: provisional / automatically created

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Zeek flow evidence is not configured for this estate.

> No absence-of-traffic conclusion is made when the Zeek source is unavailable.
<!-- END AUTO:ZEEK-FLOW -->

## Internet / DNS activity

Use bounded service/domain-family summaries here, not raw browsing history. DNS resolution alone does not prove user intent.

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-11-03T18:04:04+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `60:83:e7:f3:c8:de`
- Identity confidence: **low**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Identity is conflicting: the canonical estate records this as an ASUS AiMesh wireless mesh node, while inventory, MAC vendor, Nmap, and DNS evidence point toward a TP-Link embedded device. TCP/80 is open; no exact OS is supported.

### Confirmed facts

- The canonical estate label is ASUS AiMesh node with role Wireless mesh node.
- The inventory hostname is rt-ac86u-5228.jameshouse and the telemetry hostname is rt-ac86u-5228.
- The recorded MAC vendor is TP-Link PTE.
- DNS evidence includes TP-Link cloud and Tapo-related endpoints.
- Nmap reports an lwIP fingerprint and TCP port 80 open.
- Greenbone reports zero matching actionable findings for the current IP; this does not establish that the host is vulnerability-free or fully scanned.

### Inferences

- The device is more likely associated with TP-Link embedded IoT firmware than with the documented ASUS AiMesh identity, but this cannot be resolved from the supplied evidence.
- lwIP is treated as a TCP/IP stack identification, not as a complete operating-system identification.

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
| 2026-11-03 | Provisional host record created automatically for newly assessed MAC | network discovery + AI resolver | pending review |

## Notes

-
