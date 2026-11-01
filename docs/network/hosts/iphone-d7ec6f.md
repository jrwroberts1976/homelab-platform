# iPhone

> Automatically created provisional host record from bounded discovery and AI evidence on 2026-11-01. Canonical inventory and direct telemetry remain authoritative.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.135` |
| MAC | `be:ba:54:d7:ec:6f` |
| Device / discovered name | iPhone |
| MAC vendor | Apple |
| Stable identity key | MAC |
| Identity confidence | high |

## Profiling and platform evidence

- Device type: smartphone
- Platform family: Apple mobile platform, likely iOS
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

- Assessed: `2026-11-01T16:01:00+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `be:ba:54:d7:ec:6f`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely an Apple iPhone based on the documented hostname and Apple Nmap fingerprints. Exact OS is not established because Nmap also reported alternative Apple device and macOS matches. One TCP port is open; no actionable Greenbone findings matched the current IP.

### Confirmed facts

- The documented hostname is "iPhone" in inventory and Nmap data.
- Nmap reported Apple device fingerprints, including an iOS phone match and alternative Apple TV/macOS-or-iOS matches, each at 95% accuracy.
- TCP port 49152 is open.
- DNS samples include Apple-associated domains such as gateway.icloud.com and gspe1-ssl.ls.apple.com.
- Greenbone completed successfully with zero matching actionable findings for this IP.

### Inferences

- The device is most likely an Apple iPhone.
- The platform is likely iOS, but the exact OS version is unsupported by the supplied evidence.
- The Apple-associated DNS activity is consistent with an Apple device but is not conclusive by itself.

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
| 2026-11-01 | Provisional host record created automatically for newly assessed MAC | network discovery + AI resolver | pending review |

## Notes

-
