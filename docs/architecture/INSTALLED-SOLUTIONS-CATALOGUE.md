<!-- estate-authority: IaC/inventory/estate.json -->
# Installed Solutions Catalogue

**Purpose:** Explain the major solutions currently used by the JRW Roberts homelab, what each one does, why it is used, where it runs, and which network ports matter operationally.  
**Current-state authority:** `IaC/inventory/estate.json` and `docs/architecture/CURRENT-STATE.md`  
**Reviewed:** 22 September 2026

This is the human-readable **"what have we installed, what does it do, and why is it here?"** page for the platform.

It covers major infrastructure products, applications, supporting databases, monitoring/security agents and important network services. It deliberately does **not** list every operating-system package, dependency or transient container.

For terminology such as STUN, NAT, CVE, QoD, SPAN and quorum, see the [Network Terms & Reference](../network/TERMS-AND-REFERENCE.md).

## How to read the port information

The **Address / ports** fields below show the important documented service or management endpoints.

They are **not a firewall allow-list** and they do not attempt to enumerate ephemeral source ports.

Port scope is significant:

- **LAN** — expected to be reachable from appropriate trusted LAN/VPN clients.
- **internal** — used between components on the same host/container network and not deliberately published to the LAN.
- **loopback** — bound to localhost only.
- **passive** — the product observes traffic and does not need a normal listening port for that function.
- **external** — hosted outside the homelab.

Do not expose an internal management port to the Internet merely because it is documented here.

---

# Estate overview

| Solution | What it does | Why it is used here | Runs on / address | Main port(s) |
|---|---|---|---|---|
| Proxmox VE | Hosts VMs and LXC containers | Provides the main virtualisation and guest lifecycle platform | `PROXMOX 192.168.2.70`, `Proxmox-2 192.168.2.71` | 8006/TCP web/API; 22/TCP SSH |
| Corosync / Kronosnet | Cluster membership and messaging | Provides the Proxmox cluster control plane with preferred and fallback links | Both Proxmox nodes | dedicated cluster links; not a user-facing application port |
| QDevice / QNetd | External cluster vote | Gives the two-node cluster a third vote without requiring a third hypervisor | `admin-01 192.168.2.48` | 5403/TCP |
| Chrony | Time synchronisation/NTP | Keeps logs, TLS, DNSSEC, monitoring and cluster clocks consistent without depending on a VM | `.70`, `.71` serve LAN time; clients across estate | 123/UDP |
| Pi-hole | DNS filtering and local DNS | Gives the LAN policy filtering, local naming and visibility, with two resolvers for resilience | `dns-01 192.168.2.51`, `dns-02 192.168.2.50` | 53/TCP+UDP |
| Unbound | Recursive DNS resolver | Avoids making normal resolution depend solely on an ISP/public recursive resolver and sits behind Pi-hole | `dns-01`, `dns-02` | 127.0.0.1:5335 TCP+UDP |
| ASUS RT-AC86U | Internet router, DHCP, AiMesh controller and VPN endpoint | Keeps core WAN routing/DHCP at the network edge; existing router VPN avoided another WAN-facing VM | `192.168.2.1` | OpenVPN over UDP; LAN management only |
| ASUS AiMesh | Wireless mesh | Extends managed wireless coverage using the existing ASUS edge platform | `192.168.2.181`, `192.168.2.218` | infrastructure-managed |
| HP ProCurve 2510G-24 | Managed core switch and traffic mirror source | Provides wired switching plus SPAN/mirroring needed by the passive security sensor | `192.168.2.16` | switching/SPAN; management is legacy and should remain LAN-only |
| OpenVPN | Encrypted remote administration tunnel | Provides remote homelab access without publishing Proxmox, SSH, Grafana or Pi-hole directly to the Internet | ASUS RT-AC86U `.1`; clients use `10.8.0.0/24` | UDP transport; exact WAN listener is router-profile controlled |
| Prometheus | Collects time-series metrics | Central metrics authority for hosts, services and probes | `monitor-01 192.168.2.52` | 9090/TCP |
| Grafana | Dashboards and data exploration | Gives one human-facing view over Prometheus metrics and Loki logs | `monitor-01 .52` | 3000/TCP |
| Alertmanager | Routes/groups monitoring alerts | Separates alert delivery/suppression from Prometheus rule evaluation | `monitor-01 .52` | 9093/TCP |
| Blackbox Exporter | External-style service probes | Proves that services are reachable from the network, not merely healthy internally | `monitor-01 .52` | 9115/TCP |
| Loki | Central log store | Provides queryable central logs for Grafana without turning every log line into a metric | `monitor-01 .52` | 3100/TCP |
| Grafana Alloy | Collects/forwards telemetry | Standardises log/telemetry forwarding across managed hosts | managed estate | 12345/TCP local UI/API, normally loopback |
| Node Exporter | Exposes Linux OS metrics | Gives Prometheus a consistent host-level view of CPU, memory, disks and interfaces | managed Linux estate | 9100/TCP |
| rsyslog router receiver | Receives/persists router logs | Keeps a durable first receipt point before Alloy forwards the logs to Loki | `monitor-01 .52` | 5514/UDP |
| Zabbix | Agent-based monitoring/problem platform | Adds an agent-oriented operational monitoring view alongside Prometheus | `zabbix-01 192.168.2.59` | 8080/TCP web; 10051/TCP server default |
| Zabbix Agent 2 | Host telemetry and active checks | Gives Zabbix direct host visibility across the managed Linux estate | managed Linux estate | 10050/TCP passive listener; active checks target `.59:10051` |
| PostgreSQL | Relational database | Durable application database for Nextcloud and Zabbix | `cloud-01 .53`, `zabbix-01 .59` | 5432/TCP internal/local application path |
| TimescaleDB | PostgreSQL time-series extension | Improves Zabbix history/trend storage while retaining PostgreSQL | `zabbix-01 .59` | uses PostgreSQL 5432/TCP |
| Nginx | Zabbix web frontend | Provides the web-facing frontend for the packaged Zabbix UI | `zabbix-01 .59` | 8080/TCP |
| Suricata | IDS/network security engine | Detects suspicious traffic and known signatures on mirrored packets | `sensor-01 192.168.2.55` | passive capture; no LAN application port required |
| Zeek | Network metadata/behaviour analysis | Complements Suricata by explaining who talked to whom and which protocols were observed | `sensor-01 .55` | passive capture; no LAN application port required |
| Greenbone Community | Vulnerability scanning | Actively tests LAN hosts for known vulnerabilities/configuration weaknesses | `greenbone-01 192.168.2.57` | 443/TCP web UI |
| Network Host Collector | Host discovery/enrichment | Builds operational visibility of devices seen on the LAN and feeds dashboards/notifications | `Proxmox-2 .71` | no dedicated user-facing port |
| Docker | Application container runtime | Gives selected applications repeatable, isolated deployment units | `docker-01` and selected application hosts | daemon not deliberately published to LAN |
| Komodo Core | Container-management control plane | Preferred operational path for Docker application deployment, version management and rollback ownership | `komodo-01 192.168.2.58` | 9120/TCP |
| MongoDB | Komodo database | Stores Komodo control-plane application data | internal to `komodo-01` stack | 27017/TCP internal only |
| Nextcloud | Self-hosted cloud/data application | Provides the estate's private cloud service under local operational control | `cloud-01 192.168.2.53` | 8080/TCP |
| Redis | Nextcloud cache/locking service | Improves performance and supports application locking/coordination | internal to `cloud-01` stack | 6379/TCP internal only |
| Home Assistant OS | Home automation appliance platform | Official HAOS VM gives the supported Supervisor/appliance model instead of adding HA to Docker/LXC | `home-01 192.168.2.60` | 80/TCP |
| Home Assistant Core | Automation application | Runs integrations, entities, automations and dashboards inside HAOS | `home-01 .60` | exposed through HAOS port 80 |
| BirdNET-Go | Bird-call identification application | Keeps the dedicated Raspberry Pi 4 useful as a single-purpose wildlife/audio workload | `docker-01 192.168.2.220` | 8080/TCP |
| Postfix | Central SMTP relay | Prevents every homelab application from separately owning external SMTP credentials and settings | `mail-relay-01 192.168.2.54` | 25/TCP LAN relay; outbound 587/TCP TLS |
| NFS | Network backup storage | Gives both Proxmox nodes a separate network backup target on `media-01` | `media-01 192.168.2.195` | 2049/TCP (NFSv4.2) |
| Samba / SMB | Authenticated media file sharing | Provides convenient network access to media while Kodi itself uses local paths | `media-01 .195` | 445/TCP |
| Kodi | Living-room media endpoint | Provides the local media playback workload on the Raspberry Pi 5 | `media-01 .195` | local application; no required LAN management port documented |
| Ansible | Configuration management | Makes Linux/service configuration reproducible, reviewable and idempotent | normally run from `admin-01 .48` | no daemon/listening port; uses SSH to targets |
| Terraform | Infrastructure provisioning | Defines Proxmox guests and infrastructure state as code instead of GUI-only configuration | normally run from `admin-01 .48` | no daemon/listening port; uses provider APIs |
| Git / GitHub | Source/change authority | Keeps IaC, documentation and reviewed changes version-controlled | repository-hosted externally | HTTPS/SSH outbound as configured |
| GitHub Actions | CI automation | Validates/builds selected repository workflows without another local CI server | GitHub-hosted | external HTTPS |
| Cloudflare Pages | Public website deployment | Hosts the public engineering portfolio without publishing the homelab as a web origin | Cloudflare-hosted | external HTTPS/443 |

---

# 1. Virtualisation and cluster platform

## Proxmox VE

**Runs on**

- `PROXMOX` — `192.168.2.70`
- `Proxmox-2` — `192.168.2.71`

**What it does**

Proxmox VE is the main virtualisation platform. It hosts both full virtual machines and LXC containers, manages their storage/network configuration, schedules backups and provides the cluster management plane.

**Why we use it**

It provides one platform for both VMs and lightweight LXCs and fits the estate's Git/IaC model. The two-node cluster provides coordinated management, while important guests are distributed across the two physical hosts.

**Important ports**

- `8006/TCP` — Proxmox web UI/API.
- `22/TCP` — SSH administration.
- cluster communication uses the dedicated Corosync/Kronosnet paths and is not treated as a general user-facing service.

**Important design limitation**

The guest disks remain node-local. Cluster membership and quorum therefore do **not** equal automatic storage HA.

## Corosync and Kronosnet

**What they do**

Corosync manages cluster membership and messaging. Kronosnet provides the network transport used by the cluster.

**Why we use them**

They are the Proxmox cluster control-plane mechanism and allow the estate to use:

- a preferred direct point-to-point heartbeat link;
- the normal management LAN as a fallback.

This gives the control plane a path that is not dependent on a single switched interface.

## QDevice / QNetd

**Runs on:** `admin-01 192.168.2.48`  
**Port:** `5403/TCP`

**What it does**

QNetd provides the external QDevice vote used by the two-node Proxmox cluster.

**Why we use it**

A two-node cluster benefits from an independent third vote. Using `admin-01` provides that vote without building a third Proxmox hypervisor.

The vote protects quorum decisions; it does not provide VM storage.

## LXC and virtual machines

The platform deliberately uses both.

**LXC** is preferred where a lightweight Linux service can safely share the host kernel. Current examples include DNS, mail relay, Komodo and Zabbix.

**VMs** are used where stronger isolation, an appliance OS or dedicated kernel/device behaviour is useful. Current examples include Nextcloud, monitoring, the passive sensor, Greenbone and Home Assistant.

---

# 2. Core network services

## ASUS RT-AC86U

**Address:** `192.168.2.1`

**What it does**

The router is the Internet edge and currently owns:

- WAN routing/NAT;
- DHCP;
- AiMesh control;
- router-hosted OpenVPN;
- remote syslog generation.

**Why we use it**

It already owns the network edge, so keeping DHCP and the production VPN there avoids making basic remote access depend on a Proxmox VM, Docker host or internal Linux guest.

The OpenVPN decision was made specifically to avoid adding another WAN-facing Linux service and to keep remote access available even if the virtualisation platform is unavailable.

## DHCP

DHCP is provided by the ASUS router.

It supplies ordinary clients with addressing, gateway and DNS settings. Fixed infrastructure identity/addressing is still governed by `IaC/inventory/estate.json`, not by whatever happens to appear in a DHCP lease table.

## ASUS AiMesh

**Addresses:** `192.168.2.181`, `192.168.2.218`

AiMesh extends wireless coverage while remaining under the router's wireless control plane.

## HP ProCurve 2510G-24

**Address:** `192.168.2.16`

**What it does**

This is the core managed Ethernet switch.

It also provides the SPAN/mirror source feeding `sensor-01`, with current-state architecture recording ports 1–23 mirrored to port 24.

**Why we use it**

The managed-switch capability is important because passive IDS/Zeek visibility requires packet copies from traffic that does not normally traverse the sensor.

The switch has legacy management limitations and should remain a trusted-LAN management device.

---

# 3. DNS platform

## Pi-hole

**Addresses**

- `dns-01 192.168.2.51`
- `dns-02 192.168.2.50`

**Ports:** `53/TCP` and `53/UDP`

**What it does**

Pi-hole is the LAN-facing DNS policy and local-name layer.

It provides:

- local DNS;
- domain/blocklist policy;
- visibility into DNS requests;
- a stable DNS service presented to LAN/VPN clients.

**Why we use it**

It gives central DNS policy rather than configuring filtering independently on every client. Two instances are split across the two Proxmox nodes so a single DNS guest/node failure does not have to remove all name resolution.

## Unbound

**Runs on:** both DNS containers  
**Port:** `127.0.0.1:5335` over TCP/UDP

**What it does**

Unbound performs recursive DNS resolution behind Pi-hole.

**Why we use it**

Pi-hole handles client-facing filtering/local records while Unbound performs the recursive resolver role. Keeping Unbound on loopback means it is an internal backend rather than another directly advertised resolver.

**Flow**

```text
LAN/VPN client
      |
      | DNS 53
      v
Pi-hole
      |
      | localhost:5335
      v
Unbound
      |
      v
DNS hierarchy
```

---

# 4. Monitoring, dashboards and logging

## Prometheus

**Address:** `192.168.2.52:9090`

Prometheus is the central time-series metrics engine.

**Why chosen:** it gives a pull-based metrics model that works well with Node Exporter and service exporters, and it is the current authority for host/service metrics and probes.

## Grafana

**Address:** `192.168.2.52:3000`

Grafana is the human-facing dashboard and exploration layer.

**Why chosen:** it can present Prometheus metrics and Loki logs together, allowing operations, performance and security views to share one UI without forcing one backend to do both jobs.

## Alertmanager

**Address:** `192.168.2.52:9093`

Alertmanager handles grouping, routing, inhibition and delivery of monitoring alerts.

**Why chosen:** it keeps notification policy separate from the metric collection engine.

## Blackbox Exporter

**Address:** `192.168.2.52:9115`

Blackbox Exporter actively probes endpoints such as ICMP, TCP or HTTP.

**Why chosen:** an application can believe it is healthy while clients still cannot reach it. Blackbox provides the client-side availability view.

## Loki

**Address:** `192.168.2.52:3100`

Loki stores and queries logs.

**Why chosen:** it gives central searchable logs and integrates directly with Grafana without trying to turn unstructured logs into Prometheus metrics.

## Grafana Alloy

**Runs on:** the managed baseline  
**Local UI/API:** normally `127.0.0.1:12345`

Alloy collects/forwards telemetry and is the standard log-forwarding layer.

**Why chosen:** one agent can provide a consistent Git-managed collection model across hosts, including router-log forwarding from `monitor-01`.

## Node Exporter

**Runs on:** managed Linux hosts  
**Port:** `9100/TCP`

Node Exporter exposes operating-system metrics to Prometheus.

**Why chosen:** it is a lightweight standard way to obtain CPU, memory, filesystem, load and network counters from Linux hosts.

## Router rsyslog receiver

**Address:** `192.168.2.52:5514/UDP`

The ASUS router sends remote syslog to `monitor-01`.

**Why we retain a local rsyslog file as well as Loki**

The file is the first receipt/persistence point. Alloy then forwards it to Loki. A temporary Loki or Alloy problem therefore does not have to mean the router stream was never received.

## Zabbix

**Address:** `192.168.2.59`  
**Web:** `8080/TCP`  
**Server listener:** `10051/TCP` (the IaC does not override Zabbix's standard server port)  
**Agent listener:** `10050/TCP`

**What it does**

Zabbix provides an agent-oriented monitoring/problem platform across the managed Linux estate.

**Why we use it alongside Prometheus**

The estate deliberately uses both monitoring styles:

- Prometheus is the primary metrics/scrape platform;
- Zabbix provides active-agent host monitoring and trigger/problem handling.

They are complementary rather than a requirement to duplicate every check.

## PostgreSQL + TimescaleDB on Zabbix

**Address context:** internal/local on `zabbix-01`  
**Port:** `5432/TCP`

PostgreSQL stores Zabbix data. TimescaleDB adds time-series storage capabilities supported by the deployed Zabbix design.

## Nginx on Zabbix

**Address:** `192.168.2.59:8080`

Nginx provides the Zabbix web frontend.

---

# 5. Network security and vulnerability management

## Suricata

**Host:** `sensor-01 192.168.2.55`  
**Capture:** passive mirrored NIC; no application listening port required

Suricata is the intrusion-detection/network-security engine.

**Why chosen:** it is strong at answering:

> Does this traffic match a known detection rule or suspicious pattern?

It produces structured events such as alerts, flows, DNS, TLS and protocol metadata.

## Zeek

**Host:** `sensor-01 192.168.2.55`  
**Capture:** passive mirrored NIC

Zeek is the network behaviour/metadata analysis platform.

**Why it runs alongside Suricata**

Zeek answers a different question:

> What communication and behaviour was observed?

That makes Suricata and Zeek complementary: detection plus context.

## Greenbone Community

**Host:** `greenbone-01 192.168.2.57`  
**Web UI:** `443/TCP`

Greenbone provides active vulnerability scanning of the LAN.

**Why chosen**

Passive monitoring tells us what crosses the network. Greenbone deliberately probes systems and services to find known vulnerabilities and configuration weaknesses that may not otherwise generate suspicious traffic.

The scanner remains LAN-only.

## Network Host Collector

**Host:** `Proxmox-2 192.168.2.71`

The collector discovers, enriches and profiles observed LAN hosts for inventory, dashboards and first-seen visibility.

**Why chosen**

Security monitoring is more useful when an IP/MAC can be related to an actual device and expected role.

Discovery is operational evidence; canonical infrastructure identity still lives in `IaC/inventory/estate.json`.

---

# 6. Container management

## Docker

Docker is the application container runtime used by selected workloads.

**What it gives us**

```text
image    -> packaged application
container -> running image
volume    -> persistent data
Compose   -> multi-container application definition
```

**Why used**

For suitable applications it provides reproducible packaging and simpler application upgrades than installing all application dependencies directly into the host OS.

The Docker daemon itself is not deliberately exposed as a remote unauthenticated LAN API.

## Komodo Core

**Host:** `komodo-01 192.168.2.58`  
**Port:** `9120/TCP`

Komodo is the commissioned container-management control plane.

**Why chosen**

The estate is moving routine Docker application/version management toward one controlled platform rather than maintaining multiple ad-hoc update mechanisms.

The design goal is clearer ownership of:

- deployment;
- version changes;
- rollback;
- managed-host onboarding.

## MongoDB

**Scope:** internal to the Komodo Compose stack  
**Port:** `27017/TCP` internal only

MongoDB is Komodo's application database.

It is a supporting component, not a service intended for direct LAN administration.

---

# 7. Cloud data platform

## Nextcloud

**Host:** `cloud-01 192.168.2.53`  
**Port:** `8080/TCP`

Nextcloud provides the self-hosted cloud application.

**Why chosen**

It allows file/data services to remain under local operational control while still providing a browser/application-oriented cloud experience.

The deployment deliberately separates application, database/cache and data-disk responsibilities.

## PostgreSQL for Nextcloud

**Scope:** internal Docker network on `cloud-01`  
**Port:** `5432/TCP` internal

PostgreSQL stores Nextcloud's structured application data.

**Why chosen**

It provides the durable relational database required by the cloud application. This is why a useful Nextcloud recovery must consider database state as well as the user files.

## Redis

**Scope:** internal Docker network on `cloud-01`  
**Port:** `6379/TCP` internal

Redis supplies caching/locking support.

**Why chosen**

It improves application performance and coordination without becoming the primary store for user files.

**Architecture**

```text
Client
  |
  v
Nextcloud :8080
  |
  +--> PostgreSQL :5432 (internal)
  |
  +--> Redis :6379 (internal)
  |
  +--> dedicated data disk
```

---

# 8. Home automation

## Home Assistant OS

**Host:** `home-01 192.168.2.60`  
**Port:** `80/TCP`

The deployment uses the official Home Assistant OS KVM/Proxmox image.

**Why chosen**

The official appliance model provides the supported Supervisor environment and keeps Home Assistant lifecycle management inside the HAOS platform rather than mixing it into the general Docker estate.

This also gives the workload a dedicated VM boundary.

## Home Assistant Core

Core is the actual home-automation application inside HAOS.

It provides:

- integrations;
- devices/entities;
- dashboards;
- automations;
- service/API logic.

No direct WAN exposure is approved; remote administration uses the existing VPN path.

---

# 9. Mail and notifications

## Postfix

**Host:** `mail-relay-01 192.168.2.54`  
**LAN relay:** `25/TCP`  
**External upstream:** `587/TCP` with TLS/authentication

Postfix is the central outbound mail relay.

**Why chosen**

Without a relay, every monitoring/application service would need to own its own external mail credentials, TLS settings and provider configuration.

The central path is:

```text
Homelab application
      |
      | SMTP 25
      v
mail-relay-01 / Postfix
      |
      | TLS/authenticated SMTP 587
      v
external mail provider
```

This creates one place to control and troubleshoot outbound email.

---

# 10. Media and backup services

## media-01

**Host:** Raspberry Pi 5  
**Address:** `192.168.2.195`

The host has two important roles:

1. living-room Kodi/media endpoint;
2. primary Proxmox guest-backup target.

## Kodi

Kodi is the local media playback application.

**Why chosen**

It keeps the media workload local to the television/media endpoint rather than consuming a server VM merely to render local media.

No required LAN management port is currently part of the authoritative service design.

## Samba / SMB

**Address:** `192.168.2.195`  
**Primary SMB port:** `445/TCP`

SMB provides authenticated network access to media files.

Kodi itself uses local filesystem paths rather than looping back through its own SMB share.

## NFS

**Address:** `192.168.2.195`  
**Protocol:** NFS v4.2/TCP  
**Main port:** `2049/TCP`

NFS provides the current Proxmox backup target.

**Why chosen**

Both hypervisors can write guest backup archives to storage outside their own local disks.

Separate namespaces are used for the two nodes to avoid duplicate VMID collisions.

**Important limitation**

The backup repository is still on `media-01`'s physical storage. It protects guests from a Proxmox-node disk failure, but it does not protect against loss of the `media-01` host/NVMe itself. An independent second-copy failure domain remains desirable.

---

# 11. BirdNET

## BirdNET-Go

**Host:** `docker-01 192.168.2.220`  
**Port:** `8080/TCP`

BirdNET-Go analyses audio and identifies bird calls.

**Why chosen / placement**

`docker-01` is deliberately a small single-purpose Raspberry Pi 4 application host. Keeping BirdNET there avoids adding the hobby/audio workload to critical DNS, monitoring or cluster services.

It is containerised with Docker for straightforward application packaging.

---

# 12. Time service

## Chrony

**Servers**

- `PROXMOX 192.168.2.70:123/UDP`
- `Proxmox-2 192.168.2.71:123/UDP`

**What it does**

Both physical Proxmox hosts independently synchronise upstream and serve NTP to the LAN.

**Why chosen**

Time is required before many higher-level services are trustworthy. Hosting NTP directly on the physical hypervisors avoids a circular dependency where the hypervisor would need a guest VM to boot before it could obtain reliable time.

Clients can use both hosts for resilience.

---

# 13. Remote access

## OpenVPN

**Endpoint:** ASUS RT-AC86U  
**VPN network:** `10.8.0.0/24`  
**Transport:** UDP

OpenVPN provides encrypted routed access to `192.168.2.0/24`.

**Why router-hosted OpenVPN was selected**

A dedicated WireGuard/VM approach was considered, but the router already provided a working native OpenVPN service.

Using it:

- removes the VPN dependency on either Proxmox node;
- removes dependency on Docker;
- avoids placing another Linux service directly on the WAN;
- keeps split-tunnel remote administration at the network edge.

The external listener is controlled by the router/client profile. Sensitive client profiles and credentials are not recorded in Git.

---

# 14. Administration and Infrastructure as Code

## admin-01

**Address:** `192.168.2.48`

`admin-01` is the normal control point for infrastructure work and also hosts QNetd.

Typical administration uses SSH `22/TCP` to managed systems.

## Ansible

Ansible manages operating-system and service configuration.

**Why chosen**

It makes configuration:

- declarative/repeatable;
- reviewable in Git;
- testable for idempotency;
- rebuildable after host loss.

Ansible does not require a permanent agent/listening daemon on targets; the normal transport is SSH.

## Terraform

Terraform defines/provisions Proxmox infrastructure where the repository has migrated the resource into IaC.

**Why chosen**

It separates desired infrastructure state from manual Proxmox GUI operations and makes VM/LXC creation reviewable and repeatable.

Terraform itself has no listening port; provider/API access is outbound from the controller.

## Git / GitHub

Git is the change/history mechanism and GitHub hosts the reviewed repository.

**Why chosen**

The operating principle is that migrated configuration and documentation should have a traceable source of truth rather than living only in GUIs or administrator memory.

## GitHub Actions

GitHub Actions runs selected CI/build/validation workflows.

**Why chosen**

It provides hosted automation without adding another local Jenkins/CI dependency to the current production platform.

---

# 15. Public web hosting

## Cloudflare Pages

The engineering portfolio/public web pipeline uses Cloudflare Pages.

**Location:** external/hosted  
**Access:** HTTPS `443/TCP`

**Why chosen**

Public website delivery can remain outside the homelab. A public portfolio therefore does not require opening inbound web ports to the home network.

This is separate from the reserved `edge-01` LXC.

---

# 16. Reserved but not installed

## edge-01 / Cloudflare Tunnel

**Host:** `edge-01 192.168.2.56`

The LXC exists, but **cloudflared / Cloudflare Tunnel is not deployed**.

That distinction is intentional. The presence of a reserved host must not be interpreted as an active tunnel or public-ingress path.

Tunnel deployment should happen only when there is an approved service requirement and a documented recovery/security model.

---

# 17. Cross-cutting service ports

This table is useful when troubleshooting connectivity.

| Port | Protocol | Used by | Scope / meaning |
|---:|---|---|---|
| 22 | TCP | SSH administration | trusted LAN/VPN management |
| 25 | TCP | Postfix relay | internal application mail submission |
| 53 | TCP/UDP | Pi-hole | LAN/VPN DNS |
| 80 | TCP | Home Assistant | LAN/VPN application UI |
| 123 | UDP | Chrony/NTP | LAN time service |
| 443 | TCP | Greenbone web UI; external HTTPS services | Greenbone LAN-only; external web elsewhere |
| 445 | TCP | Samba/SMB | authenticated media file sharing |
| 2049 | TCP | NFS v4.2 | Proxmox backup traffic to `media-01` |
| 3000 | TCP | Grafana | monitoring UI |
| 3100 | TCP | Loki | log API |
| 5335 | TCP/UDP | Unbound | loopback backend on DNS hosts |
| 5403 | TCP | Corosync QNetd | cluster QDevice vote |
| 5514 | UDP | Router syslog receiver | ASUS -> `monitor-01` |
| 6379 | TCP | Redis | internal Docker network only |
| 8006 | TCP | Proxmox VE | LAN/VPN management UI/API |
| 8080 | TCP | Nextcloud, Zabbix frontend, BirdNET-Go (on different hosts) | application UIs |
| 9090 | TCP | Prometheus | metrics/query UI/API |
| 9093 | TCP | Alertmanager | alert API/UI |
| 9100 | TCP | Node Exporter | Prometheus host metrics |
| 9115 | TCP | Blackbox Exporter | probe service |
| 9120 | TCP | Komodo Core | container-management UI/API |
| 10050 | TCP | Zabbix Agent 2 | passive agent checks where used |
| 10051 | TCP | Zabbix Server | active-agent/server traffic |
| 12345 | TCP | Grafana Alloy | local/loopback UI/API |
| 27017 | TCP | MongoDB | internal Komodo network |
| 5432 | TCP | PostgreSQL | internal/local application database traffic |

The same port can legitimately appear on several different hosts. `8080/TCP`, for example, is used by multiple independent applications, which is not a conflict because each service has its own IP address.

---

# 18. Host-to-solution map

| Host | Address | Main installed/hosted solutions |
|---|---:|---|
| `admin-01` | `192.168.2.48` | administration/IaC controller, SSH jump role, QNetd, managed baseline agents |
| `dns-02` | `192.168.2.50` | Pi-hole, Unbound, monitoring/logging agents |
| `dns-01` | `192.168.2.51` | Pi-hole, Unbound, monitoring/logging agents |
| `monitor-01` | `192.168.2.52` | Prometheus, Grafana, Alertmanager, Blackbox Exporter, Loki, Alloy, rsyslog receiver |
| `cloud-01` | `192.168.2.53` | Nextcloud, PostgreSQL, Redis, Docker, managed agents |
| `mail-relay-01` | `192.168.2.54` | Postfix SMTP relay, managed agents |
| `sensor-01` | `192.168.2.55` | Suricata, Zeek, Alloy, Node Exporter, managed agents |
| `edge-01` | `192.168.2.56` | reserved edge LXC and baseline only; cloudflared not deployed |
| `greenbone-01` | `192.168.2.57` | Greenbone Community scanner and supporting container stack |
| `komodo-01` | `192.168.2.58` | Docker, MongoDB, Komodo Core |
| `zabbix-01` | `192.168.2.59` | PostgreSQL, TimescaleDB, Zabbix Server, Agent 2, Nginx |
| `home-01` | `192.168.2.60` | Home Assistant OS, Supervisor, Home Assistant Core |
| `PROXMOX` | `192.168.2.70` | Proxmox VE, Corosync/Kronosnet, Chrony, managed agents |
| `Proxmox-2` | `192.168.2.71` | Proxmox VE, Corosync/Kronosnet, Chrony, Network Host Collector, managed agents |
| `media-01` | `192.168.2.195` | Kodi, Samba/SMB, NFS backup target, managed agents |
| `docker-01` | `192.168.2.220` | Docker, BirdNET-Go, managed agents |
| ASUS RT-AC86U | `192.168.2.1` | routing/NAT, DHCP, AiMesh control, OpenVPN, syslog source |
| HP ProCurve 2510G-24 | `192.168.2.16` | managed switching, SPAN/mirroring |
| ASUS AiMesh nodes | `.181`, `.218` | wireless mesh |

---

# 19. Design principles visible in the product choices

The products are not intended to form a collection of tools for their own sake. Several repeated design principles explain the choices.

**Separate functions where failure domains matter.** Monitoring and passive sensing are on different guests/physical Proxmox nodes. DNS has two resolvers. QNetd is outside the two hypervisors.

**Use complementary tools where they answer different questions.** Prometheus and Zabbix are different monitoring models. Suricata and Zeek are detection versus behavioural context. Pi-hole and Unbound are policy/local DNS versus recursive resolution.

**Do not expose internal management interfaces unnecessarily.** Remote administration enters through OpenVPN. Proxmox, Grafana, Pi-hole and other management interfaces remain LAN/VPN services.

**Keep stateful supporting services private where possible.** Redis, PostgreSQL and MongoDB are application backends rather than public LAN services unless a design specifically requires otherwise.

**Prefer Git/IaC over undocumented GUI state.** Proxmox provisioning, Linux configuration, monitoring and service definitions are increasingly represented in Terraform/Ansible/Compose/Komodo resources.

**Recovery matters as much as installation.** A product being healthy is not treated as proof that it can be recovered. The backup/recovery documentation and evidence remain separate operational requirements.

---

# Related documentation

- [Current-State Architecture](CURRENT-STATE.md)
- [Network Terms & Reference](../network/TERMS-AND-REFERENCE.md)
- [Runbook Catalogue](../../runbooks/README.md)
- [Monitoring Service](../../production%20docs/MONITORING-SERVICE.md)
- [Network Sensor Service](../../production%20docs/NETWORK-SENSOR-SERVICE.md)
- [DNS Service Recovery Plan](../../production%20docs/DNS-SERVICE-RECOVERY-PLAN.md)
- [Cloud Data Service](../../production%20docs/CLOUD-SERVICE.md)
- [Greenbone Service](../../production%20docs/GREENBONE-SERVICE.md)
- [Mail Relay Service](../../production%20docs/MAIL-RELAY-SERVICE.md)
- [BirdNET-Go Service](../../production%20docs/BIRDNET-SERVICE.md)
- [media-01 Service](../../production%20docs/MEDIA-SERVICE.md)
- [Time Service](../../production%20docs/TIME-SERVICE.md)
- [VPN Remote-Access Design](../network/VPN-REMOTE-ACCESS-DESIGN.md)
- [Proxmox Backup Recovery](../../production%20docs/PROXMOX-BACKUP-RECOVERY.md)

# Maintenance rule

When a major solution is installed, retired, replaced, moved to a new address, or given a materially different service port, update this catalogue in the same reviewed change as the authoritative current-state/IaC update.

Historical host names such as `DietPi`, `TestServer`, `ids-01` and the former `k3s-node-01` identity must not be reintroduced as current solutions.
