<!-- estate-authority: IaC/inventory/estate.json -->
# VPN Remote-Access Design and Implementation Record

**Status:** implementation active; router-hosted OpenVPN selected and externally authenticated  
**Reviewed:** 16 September 2026  
**Primary implementation:** ASUS RT-AC86U OpenVPN Server 1  
**VPN subnet observed:** `10.8.0.0/24`  
**Internal DNS:** `192.168.2.51`, `192.168.2.50`

## Goal

Provide secure remote administrative access to the homelab without publishing Proxmox, Grafana, SSH, Pi-hole or other internal management interfaces directly to the Internet.

The selected operating model is:

```text
Remote client
    |
    | OpenVPN over UDP
    v
ASUS RT-AC86U 192.168.2.1
    |
    | routed split-tunnel access
    v
192.168.2.0/24 internal services
```

The VPN is an administration path, not a mechanism for making internal services public and not a general Internet-egress VPN.

## Architecture decision

The previous design proposed a dedicated Debian `vpn-01` VM running WireGuard. During implementation discovery on 16 September 2026, the existing ASUS router was found to already have a native OpenVPN server running.

The production direction is therefore **router-hosted OpenVPN** rather than a new VM, container or host-level WireGuard service.

This choice removes the VPN's dependency on:

- either Proxmox node;
- any Proxmox guest;
- `docker-01` and Docker;
- `admin-01` and the IaC/QNetd control plane.

It also avoids adding a WAN-facing service to an internal Linux host and avoids Docker firewall/routing interaction on `docker-01`.

The trade-off is that VPN availability is now part of the router failure domain. Router backup/rebuild documentation must therefore preserve the VPN configuration and recovery path.

## Current validated state

Validated live on 16 September 2026:

- ASUS RT-AC86U at `192.168.2.1`;
- firmware `386.14_2`;
- OpenVPN Server 1 reports **Running**;
- a recreated VPN account was successfully authenticated from an external client;
- the OpenVPN server allocated client address `10.8.0.3` during the observed test session;
- the server pushed route `192.168.2.0/24` to the client;
- the server pushed internal DNS `192.168.2.51` and `192.168.2.50`;
- the observed transport was UDP;
- the observed control channel negotiated TLS 1.3 with `TLS_AES_256_GCM_SHA384`;
- the observed data channel used `AES-256-GCM`;
- router OpenVPN events are present in the router's remote syslog stream on `monitor-01`;
- those router logs are shipped to Loki through the dedicated Alloy router-syslog pipeline.

The external client authenticated and established a tunnel. Full acceptance still requires explicit proof that intended internal management services are reachable over that external tunnel and that DDNS survives WAN-address changes.

## Addressing and routing

Observed OpenVPN client addressing uses:

```text
VPN network: 10.8.0.0/24
router VPN gateway: 10.8.0.1
example assigned client: 10.8.0.3
```

The router currently pushes:

```text
192.168.2.0/24
```

as the internal LAN route.

Internal DNS supplied to VPN clients is:

```text
192.168.2.51  dns-01
192.168.2.50  dns-02
```

Do not add a competing WireGuard subnet or NAT path while this router-hosted implementation is the selected production design.

## Dynamic WAN address and DDNS

The client configuration should use a stable DDNS hostname rather than depending on a numeric WAN address.

Required completion gate:

1. confirm the ASUS DDNS client is enabled;
2. record the selected hostname without recording any DDNS secret;
3. confirm the exported `.ovpn` profile references the stable hostname;
4. prove an external connection after a WAN-address change or equivalent DDNS resolution validation.

If the exported profile contains a numeric WAN address, regenerate/export it after DDNS is configured rather than hand-maintaining multiple divergent profiles.

## Client and credential model

- use an individual VPN account per person rather than a shared account;
- use a strong VPN-specific password, not the router administrator password;
- revoke an account promptly when access is no longer required;
- export a fresh client profile after material server configuration changes;
- treat exported `.ovpn` files as sensitive recovery/access material;
- do not commit `.ovpn` profiles, passwords, certificate private material or router configuration exports containing secrets to Git;
- avoid posting client profiles in tickets, chat or documentation.

The router-generated `.ovpn` profile contains the CA/certificate material required by the client and must be distributed through a protected channel.

## Access policy

The initial service remains split tunnel and is intended for administration of the homelab.

Expected initial destinations include:

```text
admin-01    192.168.2.48
monitor-01  192.168.2.52
PROXMOX     192.168.2.70
Proxmox-2   192.168.2.71
```

The presence of the LAN route does not justify exposing these services directly on the WAN. Router administration, Proxmox management, SSH and Grafana should remain reachable through trusted LAN/VPN paths only.

## Logging and observability

The existing router logging path is part of the VPN operational design:

```text
ASUS RT-AC86U
    |
    | remote syslog UDP/5514
    v
monitor-01
    |
    +--> /var/log/homelab/router/rt-ac86u.log
    |
    +--> Grafana Alloy
             |
             v
            Loki
```

The live Alloy configuration uses stable labels from the dedicated `monitor_router_alloy` role, including:

```text
job="network-infrastructure"
service="router-syslog"
device="rt-ac86u"
environment="homelab"
```

OpenVPN authentication, connection, address-allocation and disconnect messages are therefore queryable centrally without deploying another collector on the router.

Avoid creating high-cardinality Loki labels from usernames, public client IP addresses, ports or PIDs. Those values belong in log content, not labels.

## Router recovery dependency

Because the VPN terminates on the router, any clean-reset/rebuild procedure must preserve or deliberately recreate:

- OpenVPN server enablement;
- server advanced settings;
- VPN users;
- certificate/CA identity as appropriate for the recovery method;
- DDNS configuration;
- internal route/DNS advertisement;
- router remote syslog destination `192.168.2.52:5514`;
- a fresh exported client profile after rebuild if server identity changes.

Router administrator credentials, VPN passwords and protected certificate/private-key material must remain outside Git.

## Remaining implementation gates

### Gate 1 — external management-path proof

From mobile data or another genuinely external network:

- connect using the recreated VPN account;
- prove expected access to `admin-01`;
- prove expected access to both Proxmox management interfaces;
- prove expected access to `monitor-01`/Grafana as required;
- prove both internal DNS resolvers answer through the VPN;
- confirm no extra WAN management ports were introduced.

### Gate 2 — DDNS proof

- confirm ASUS DDNS state and hostname;
- confirm the client profile uses that hostname;
- verify external name resolution to the current WAN address;
- reconnect externally using the DDNS endpoint.

### Gate 3 — observability proof

- query Loki for the successful OpenVPN authentication/connection event;
- confirm disconnect/failure messages are also retained;
- keep the local router syslog file as the first receipt point;
- add alerting only if a low-noise, actionable condition is identified.

### Gate 4 — recovery proof

- capture the non-secret router settings required to rebuild the service;
- confirm how server certificates/identity are recovered or regenerated;
- verify account deletion/recreation;
- document the client re-enrolment procedure after router replacement/reset.

## Acceptance criteria

The remote-access project is complete when:

- router-hosted OpenVPN remains running after normal router restart;
- an external client can authenticate and establish the tunnel;
- intended internal administration destinations are reachable externally through the tunnel;
- both internal DNS resolvers work through the VPN;
- DDNS provides the stable endpoint and is represented correctly in the client profile;
- no Proxmox, SSH, Grafana, Pi-hole or other management interface is directly exposed to the Internet;
- router/OpenVPN events are visible in Loki;
- VPN account revocation/recreation is documented and proven;
- router recovery documentation includes the VPN;
- sensitive client/server material remains outside Git.

## Rollback

If the router-hosted VPN causes unexpected behaviour:

1. disable OpenVPN Server 1 in the router UI;
2. confirm normal LAN, DHCP, DNS, AiMesh and WAN operation;
3. retain relevant router/Loki logs for diagnosis;
4. do not alter unrelated router services merely to troubleshoot VPN access;
5. re-enable only after the configuration issue is understood.

## Superseded implementation work

The following design paths are no longer the selected production implementation:

- dedicated `vpn-01` Debian VM;
- WireGuard on `docker-01`;
- WireGuard on `admin-01`.

The unmerged `feature/docker-01-wireguard` branch was created during exploration and must not be treated as deployed state. It can be removed after this router-hosted design change is reviewed and merged.

No `vpn-01` asset, VMID or LAN address should be added to the canonical estate for this implementation.
