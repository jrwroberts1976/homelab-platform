# Network Terms & Reference

This page is a plain-English reference for terms, protocols and security events that appear in the JRW Roberts homelab documentation, dashboards, logs and alerts.

It is intended to help a reader understand **what a term means, why it appears on this network, and whether it is normally expected or worth investigating**.

> This is a reference guide, not an alert-severity policy. Context matters: an otherwise normal protocol can still be interesting when it appears from the wrong device, at an unusual volume, or alongside other suspicious activity.

## Quick reference

| Term | Plain-English meaning | Where it is relevant here | Normally concerning? |
|---|---|---|---|
| STUN | Helps applications discover how they appear through NAT so they can establish direct connections | Suricata/Zeek events on `sensor-01`; voice/video/WebRTC traffic | Usually no |
| NAT | Translates private LAN addresses to the router's public Internet address | ASUS router, VPN and outbound Internet traffic | No |
| DNS | Converts names such as `home-01` into IP addresses | `dns-01`, `dns-02`, Pi-hole and Unbound | No |
| DHCP | Automatically gives devices their LAN IP configuration | ASUS router | No |
| ARP | Maps an IPv4 address to a local Ethernet MAC address | LAN discovery, troubleshooting and host inventory | No |
| ICMP | Network control/diagnostic protocol used by tools such as `ping` | Monitoring, troubleshooting and network scans | Usually no |
| TCP | Reliable connection-oriented transport used by web, SSH, SMTP and many other services | Across the estate | No |
| UDP | Connectionless transport often used by DNS, STUN, streaming and discovery protocols | Across the estate | No |
| SPAN / Port Mirroring | Copies switch traffic to a monitoring port | HP ProCurve -> `sensor-01` | Expected |
| IDS | Detects potentially suspicious network activity | Suricata on `sensor-01` | The IDS itself is expected; individual alerts need context |
| CVE | Public identifier for a known software vulnerability | Greenbone vulnerability reports | Depends on the CVE |
| CVSS | Numerical severity score for a vulnerability | Greenbone reports | Higher scores generally deserve more attention |
| QoD | Greenbone's confidence in a vulnerability detection | Greenbone reports | Not a severity score |
| Prometheus | Collects time-series metrics | `monitor-01` | Expected |
| Grafana | Displays metrics and logs in dashboards | `monitor-01` | Expected |
| Loki | Central log store queried by Grafana | `monitor-01` | Expected |
| Blackbox Exporter | Tests services from the outside, for example HTTP or ICMP reachability | `monitor-01` | Expected |
| QDevice / QNetd | Supplies an external vote to help a two-node Proxmox cluster maintain safe quorum | `admin-01` and the Proxmox cluster | Expected |

---

## STUN — Session Traversal Utilities for NAT

**What it is**

STUN is a networking protocol used by applications that need to establish direct connections through a router performing NAT.

A device can ask a STUN server:

- what public IP address it appears to be using;
- which public UDP port the router has mapped for it;
- and, indirectly, how the NAT/firewall is behaving.

**Why it appears on this network**

STUN is common in applications that use real-time peer-to-peer or media connections, including:

- Microsoft Teams;
- WebRTC browser applications;
- voice and video calling;
- some messaging applications;
- gaming;
- VoIP software.

A simplified flow is:

```text
Laptop / phone
      |
      | STUN request
      v
Internet STUN server
      |
      | "I see you as public-IP:port"
      v
Application uses that information to establish its connection
```

STUN commonly uses **UDP 3478**, although applications can use other ports.

On this homelab, STUN may be identified by **Suricata or Zeek on `sensor-01`** because that system receives mirrored network traffic from the HP ProCurve switch.

**Is it a security problem?**

Usually, no.

STUN by itself is not evidence of compromise. It becomes more interesting when:

- a server that should not use voice/video/WebRTC suddenly generates STUN traffic;
- there is an unexpectedly large amount of it;
- destinations are unusual;
- or it appears alongside other suspicious network events.

---

## NAT — Network Address Translation

**What it is**

NAT allows many devices using private IP addresses, such as `192.168.2.x`, to share a public Internet address.

The router keeps track of which internal connection belongs to which external connection.

**Why it matters here**

The ASUS RT-AC86U performs NAT for normal Internet access. NAT is also why protocols such as STUN exist: Internet applications need a way to discover what address and port the router has exposed for a connection.

**Normally concerning?**

No. NAT is a normal part of this network's Internet edge.

---

## DNS — Domain Name System

**What it is**

DNS converts names into IP addresses.

For example:

```text
home-01 -> 192.168.2.60
```

**Why it matters here**

The homelab uses two internal DNS services:

- `dns-01`
- `dns-02`

Both run **Pi-hole + Unbound**.

Pi-hole applies DNS filtering and local naming. Unbound performs recursive DNS resolution.

**Useful clue when troubleshooting**

If a service works when accessed by IP address but fails when accessed by hostname, DNS is one of the first things to check.

---

## DHCP — Dynamic Host Configuration Protocol

**What it is**

DHCP automatically supplies devices with settings such as:

- IP address;
- subnet mask;
- default gateway;
- DNS servers.

**Why it matters here**

The ASUS router provides DHCP for the LAN.

Servers and infrastructure with fixed identities are documented separately in the estate inventory so DHCP should not be treated as the authority for infrastructure naming or allocation.

---

## ARP — Address Resolution Protocol

**What it is**

ARP answers the local-network question:

> "Which MAC address currently owns this IPv4 address?"

For example:

```text
192.168.2.55 -> aa:bb:cc:dd:ee:ff
```

**Why it appears here**

ARP is useful for:

- device discovery;
- validating whether a host is actually present;
- correlating IP addresses with physical/network interfaces;
- troubleshooting duplicate or unexpected addresses.

Normal ARP activity is expected on every IPv4 Ethernet LAN.

---

## ICMP — Internet Control Message Protocol

**What it is**

ICMP carries network status and diagnostic messages.

The best-known example is `ping`, which normally uses ICMP Echo Request and Echo Reply messages.

**Why it appears here**

Prometheus/Blackbox monitoring, administrators, scanners and troubleshooting tools may all generate ICMP traffic.

**Is ICMP traffic suspicious?**

Not by itself.

Repeated scanning, unusual ICMP message types or unexpected Internet-originated activity can still be worth investigating.

---

## TCP — Transmission Control Protocol

**What it is**

TCP creates a reliable connection between two systems. It tracks packet ordering, retransmits missing data and detects connection state.

Common TCP-based services in this environment include:

- HTTP/HTTPS;
- SSH;
- SMTP;
- Proxmox web administration;
- Zabbix;
- many database connections.

A TCP event therefore describes the transport being used, not whether the traffic is safe or unsafe.

---

## UDP — User Datagram Protocol

**What it is**

UDP sends individual datagrams without first establishing a TCP-style session.

It is lightweight and is commonly used where low latency matters.

Examples include:

- DNS;
- STUN;
- some streaming/media traffic;
- discovery protocols;
- parts of monitoring and network infrastructure.

UDP traffic is not inherently suspicious.

---

## SPAN / Port Mirroring

**What it is**

SPAN, also called **port mirroring**, tells a managed switch to copy traffic seen on selected ports to a monitoring port.

The monitoring system can then inspect that traffic without being directly in the communication path.

**How it is used here**

The HP ProCurve switch mirrors traffic from the production switch ports to the sensor connection used by `sensor-01`.

`sensor-01` can therefore run Suricata and Zeek passively.

This is why the sensor can observe conversations between other systems even when neither endpoint is the sensor itself.

---

## Suricata

**What it is**

Suricata is a network intrusion detection and network security monitoring engine.

It can identify:

- protocols;
- applications;
- known attack patterns;
- suspicious behaviour;
- malformed traffic;
- network metadata.

**How it is used here**

Suricata runs on `sensor-01` against the mirrored traffic feed.

An event from Suricata does **not automatically mean an attack succeeded**. Some records are simple protocol identification; others are signatures that require investigation.

---

## Zeek

**What it is**

Zeek is a network analysis platform that produces detailed metadata about network conversations.

Where Suricata is particularly useful for signatures and security alerts, Zeek is often useful for answering questions such as:

- which systems communicated;
- which DNS names were queried;
- which protocols were used;
- when a connection started and ended.

Both tools can describe the same traffic from different perspectives.

---

## IDS — Intrusion Detection System

**What it is**

An IDS monitors activity and raises events or alerts when behaviour matches detection logic.

In this environment, Suricata forms the main network IDS capability on `sensor-01`.

**Important distinction**

An IDS alert means:

> "This activity matched a detection rule."

It does not necessarily mean:

> "A system was compromised."

The source, destination, rule, frequency and surrounding events should be considered together.

---

## CVE — Common Vulnerabilities and Exposures

**What it is**

A CVE is a public identifier assigned to a known security vulnerability.

It normally looks like:

```text
CVE-2026-12345
```

**Why it appears here**

Greenbone uses vulnerability information including CVEs when reporting weaknesses found during scans.

A CVE identifier makes it easier to cross-reference a finding with vendor advisories, patches and technical research.

---

## CVSS — Common Vulnerability Scoring System

**What it is**

CVSS gives a vulnerability a numerical severity score, normally from **0.0 to 10.0**.

It helps describe the technical severity of a vulnerability.

**Important limitation**

A high CVSS score does not automatically mean it is the highest operational risk in this homelab.

Real risk also depends on factors such as:

- whether the affected service is reachable;
- whether exploitation requires authentication;
- whether an exploit is practical;
- whether the system contains important data;
- compensating controls;
- whether the finding is actually applicable.

---

## QoD — Quality of Detection

**What it is**

Greenbone uses **Quality of Detection** to indicate confidence that a finding is genuinely present.

QoD is **not the vulnerability severity**.

For example, a high-severity finding with weak detection confidence should be interpreted differently from a well-confirmed finding.

---

## Prometheus

**What it is**

Prometheus collects numeric, time-series metrics.

Examples include:

- CPU usage;
- memory consumption;
- disk space;
- service availability;
- patch/update state;
- application-specific measurements.

In this estate Prometheus runs on `monitor-01`.

---

## Grafana

**What it is**

Grafana turns monitoring data into dashboards, graphs, tables and alert views.

Grafana itself is not normally the system collecting the original information. It queries sources such as:

- Prometheus for metrics;
- Loki for logs.

This distinction is useful when troubleshooting a dashboard: the problem may be Grafana, the data source, the collector or the target being monitored.

---

## Loki

**What it is**

Loki is the central log platform used by the monitoring stack.

Logs can be labelled by properties such as host, service or job and then searched from Grafana.

Examples include router and service logs forwarded into the monitoring platform.

---

## Grafana Alloy

**What it is**

Grafana Alloy is an agent used to collect and forward telemetry such as logs and metrics.

On this estate it is deployed across managed systems and is one of the mechanisms that sends data toward the central monitoring platform.

A useful mental model is:

```text
Host / application
      |
      v
Grafana Alloy
      |
      +---- metrics/logs ----> monitoring platform
```

---

## Blackbox Exporter

**What it is**

Blackbox Exporter checks a service from the perspective of a client rather than asking the service for its own internal metrics.

Examples include:

- can the host be pinged?
- does the HTTP endpoint answer?
- does TLS negotiation work?
- how long did the response take?

This is useful because a service can report that it is healthy internally while still being unreachable from the network.

---

## Pi-hole

**What it is**

Pi-hole is the DNS filtering layer used by `dns-01` and `dns-02`.

It can block DNS requests for domains on configured blocklists and provides local DNS functionality.

A Pi-hole blocked-domain event therefore usually means a client attempted to resolve a domain covered by policy; it does not on its own establish that the client is infected.

---

## Unbound

**What it is**

Unbound is the recursive DNS resolver behind Pi-hole.

Rather than relying solely on a public DNS resolver supplied by an ISP or large provider, Unbound can recursively obtain DNS information from the DNS hierarchy.

In simplified form:

```text
Client
  |
  v
Pi-hole
  |
  v
Unbound
  |
  v
DNS hierarchy
```

---

## OpenVPN

**What it is**

OpenVPN creates an encrypted network tunnel between a remote device and the home network.

The production remote-access VPN is hosted by the ASUS router.

A connected VPN client receives an address from the VPN range and can access permitted LAN services as though it has a routed path into the home network.

---

## Split tunnelling

**What it is**

Split tunnelling means only selected traffic is sent through a VPN.

In the current remote-access design:

- homelab traffic travels through OpenVPN;
- ordinary Internet traffic continues to use the client's local Internet connection.

This differs from a full-tunnel VPN, where all client Internet traffic is routed through the home network.

---

## Proxmox quorum

**What it is**

Quorum is the mechanism that determines whether enough cluster votes are available for Proxmox/Corosync to make safe cluster decisions.

The estate has two Proxmox nodes and an external QDevice vote.

Quorum protects the **cluster control plane** from split-brain-style decisions. It does not mean that VM disks stored locally on a failed node automatically become available on the remaining node.

---

## QDevice / QNetd

**What it is**

A QDevice provides an additional vote to a Corosync cluster.

Here, `admin-01` runs **QNetd**, providing the third vote used by the two-node Proxmox cluster.

Simplified:

```text
PROXMOX -----+
             |
Proxmox-2 ---+---- cluster voting
             |
admin-01 ----+---- QDevice/QNetd vote
```

This improves quorum behaviour if one Proxmox node becomes unavailable, provided the remaining node can still reach the QDevice.

---

## LXC / Container

**What it is**

An LXC container shares the host Linux kernel while providing an isolated user-space environment.

It is lighter than a full virtual machine.

Examples in the current estate include `dns-01`, `dns-02`, `zabbix-01` and `komodo-01`.

---

## VM — Virtual Machine

**What it is**

A virtual machine emulates a complete computer and runs its own operating-system kernel.

Examples in the current estate include `monitor-01`, `sensor-01`, `greenbone-01`, `cloud-01` and `home-01`.

---

## Greenbone

**What it is**

Greenbone is the vulnerability-management platform running on `greenbone-01`.

It actively scans systems and services looking for known vulnerabilities and configuration weaknesses.

This is different from `sensor-01`:

- **Greenbone** actively probes hosts;
- **Suricata/Zeek** passively observe mirrored network traffic.

Knowing that distinction helps explain why Greenbone traffic can look like scanning: scanning is its intended job.

---

## Common interpretation rule

When an unfamiliar event appears in Grafana, Loki, Suricata, Zeek or Greenbone, a useful first assessment is:

1. **What protocol or product generated the event?**
2. **Which internal host generated the traffic?**
3. **What was the destination?**
4. **Is that behaviour expected for that host's role?**
5. **How often is it happening?**
6. **Is it only protocol identification, or an actual security signature/finding?**
7. **Are there related events immediately before or after it?**

The most important question is usually not simply **"Is this protocol dangerous?"**, but:

> **"Is this behaviour expected from this particular device in this particular context?"**

---

## Related documentation

- [Current-State Architecture](../architecture/CURRENT-STATE.md)
- [VPN Remote-Access Design](VPN-REMOTE-ACCESS-DESIGN.md)
- [Switch Port Map](SWITCH-PORT-MAP.md)
- [Network Sensor Service](../../production%20docs/NETWORK-SENSOR-SERVICE.md)
- [Monitoring Service](../../production%20docs/MONITORING-SERVICE.md)
- [Greenbone Vulnerability Scanner Service](../../production%20docs/GREENBONE-SERVICE.md)

## Maintaining this page

Add a term when:

- it appears repeatedly in dashboards or logs;
- a reader could reasonably mistake normal behaviour for a security incident;
- it is specific to the architecture and needs local context;
- or understanding it makes another runbook/design document easier to follow.

Definitions should remain short, practical and tied to the current estate rather than becoming a generic networking textbook.
