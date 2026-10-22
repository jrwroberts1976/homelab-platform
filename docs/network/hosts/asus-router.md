# asus-router

> Persistent private host record. Keep secrets and raw packet/DNS captures out of Git.

## Identity

| Field | Value |
|---|---|
| Canonical name | `asus-router` |
| Address | `192.168.2.1` |
| Type | network |
| Role | ASUS RT-AC86U router, DHCP, AiMesh controller and OpenVPN remote-access endpoint |
| Managed by Ansible | No |
| State | Active |

## Network identity
- MAC address:
- Vendor/OUI:
- Hostname / DHCP name:
- VLAN / network:
- Physical location or hypervisor:

## Operating system and platform evidence
- Authoritative OS:
- OS evidence source:
- Architecture:
- Kernel / firmware:
- Nmap fingerprint:
- Nmap evidence timestamp:
- Confidence / review status:

## Open ports and services
| Port | Protocol | Service | Product/version | Evidence time | Expected? |
|---:|---|---|---|---|---|
| | | | | | |

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
Use bounded domain/service summaries only; do not commit a complete household browsing history.

| Service / domain family | Example domains | Evidence source | Last observed | Interpretation |
|---|---|---|---|---|
| | | | | |

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-22T13:00:41+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `24:4b:fe:5e:cc:c8`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

ASUS RT-AC86U router at 192.168.2.1, serving as the estate gateway, DHCP/AiMesh controller, and OpenVPN remote-access endpoint. Exact firmware/OS is not identified by the supplied evidence.

### Confirmed facts

- The canonical estate identifies this device as ASUS RT-AC86U with the name asus-router.
- The canonical role is Router, DHCP, AiMesh controller and OpenVPN remote-access endpoint.
- The inventory vendor is ASUSTek Computer and the inventory hostname is _gateway.
- The device IP is 192.168.2.1 and it is currently online.
- TCP/22 exposes Dropbear SSH protocol 2.0.
- TCP/53 exposes Cloudflare public DNS.
- TCP/80 is open; the Nmap service label is omitted.
- TCP/8443 exposes HTTPS-alt with TLS.
- The TLS certificate subject is jrwroberts1976.asuscomm.com and is issued by Let's Encrypt.
- No actionable Greenbone findings match the current host IP in the supplied scan results.

### Inferences

- The device is an embedded consumer-router platform rather than a general-purpose server.
- The documented gateway role and router model provide high-confidence device identification.
- The exact operating system or firmware version cannot be determined from the supplied evidence.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

## Monitoring and security
- Grafana host dashboard:
- Zabbix / Node Exporter / other monitoring:
- Alerting:
- Vulnerability findings:
- Firewall/access policy:
- Accepted risks:

## Ownership and administration
- Owner / responsible person:
- Management method:
- Configuration source:
- Patching / maintenance:
- Backup / recovery:
- Planned retirement / replacement:

## Evidence history
| Date | Evidence / change | Source | Reviewed by |
|---|---|---|---|
| | | | |

## Notes
- 
