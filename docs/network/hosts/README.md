# Network host records

This directory contains one persistent, editable Markdown record per known
network host/device.

The host pages are intentionally separate from transient scan evidence. Their
purpose is to keep a long-lived operational record that can be enriched over
time with identity, OS/firmware, open ports, expected and observed network
flows, bounded DNS/Internet service evidence, monitoring, security findings,
ownership and change history.

Do **not** commit passwords, API tokens, recovery material, raw packet
captures, or a complete household browsing history. For Internet activity,
prefer bounded service/domain-family summaries and a few representative
domains with timestamps and evidence source.

## Managed / canonical hosts

- [admin-01](admin-01.md)
- [dns-02](dns-02.md)
- [dns-01](dns-01.md)
- [monitor-01](monitor-01.md)
- [cloud-01](cloud-01.md)
- [mail-relay-01](mail-relay-01.md)
- [sensor-01](sensor-01.md)
- [edge-01](edge-01.md)
- [greenbone-01](greenbone-01.md)
- [komodo-01](komodo-01.md)
- [zabbix-01](zabbix-01.md)
- [home-01](home-01.md)
- [PROXMOX](proxmox.md)
- [Proxmox-2](proxmox-2.md)
- [media-01](media-01.md)
- [docker-01](docker-01.md)
- [ASUS router](asus-router.md)
- [ASUS AiMesh 192.168.2.181](asus-aimesh-181.md)
- [ASUS AiMesh 192.168.2.218](asus-aimesh-218.md)
- [HP ProCurve 2510G-24](hp-procurve-2510g-24.md)

## Discovered / evidence-qualified devices

- [Amazon Fire TV / Fire TV Stick — 192.168.2.8](mac-94-3a-91-cd-4c-51.md)
- [Unidentified device — 192.168.2.130](mac-14-7f-67-6d-e5-98.md)

## Information to maintain per host

Each page has sections for:

- stable identity: hostname, IP, MAC and vendor/OUI;
- authoritative and inferred OS/firmware evidence;
- positively observed open ports and services;
- expected and observed network flows;
- Internet/DNS service activity;
- monitoring and security findings;
- ownership, maintenance and recovery information;
- dated evidence/change history.

### Network-flow records

Record useful summaries such as:

```text
device -> dns-01/dns-02 : UDP/TCP 53 : DNS resolution
monitor-01 -> host      : TCP 9100    : Node Exporter scrape
host -> mail-relay-01   : TCP 25      : SMTP relay
```

For passive Zeek/Suricata evidence, record the flow purpose and observation
window rather than copying raw logs into Git.

### Internet / browsing evidence

For infrastructure and appliance hosts, this section usually represents
application/cloud dependencies rather than human web browsing. Examples:

```text
Amazon Fire TV / Video
  ftvpes-eu.amazon.com
  *.api.amazonvideo.com

NordVPN
  pdp.nordvpn.com
  nc-mqtt.nordvpn.com
```

Use this evidence to explain what a device appears to be doing. Domain
resolution alone does not prove the user visited a site, and a DNS clue must
not be promoted to authoritative device identity without corroboration.

## Adding newly discovered devices

New unmanaged devices should use their stable MAC as the filename until a
reviewed friendly/canonical identity exists:

```text
mac-aa-bb-cc-dd-ee-ff.md
```

When the IP changes, update the same MAC-keyed page rather than creating a
second page. Once a device is formally named, the page can be renamed during a
reviewed Git change while retaining its evidence history.
