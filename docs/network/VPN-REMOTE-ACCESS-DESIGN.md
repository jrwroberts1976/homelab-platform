# VPN Remote-Access Design and Project Plan

**Status:** approved design / planned implementation  
**Reviewed:** 15 September 2026  
**Primary design:** dedicated `vpn-01` Debian VM running WireGuard  
**Secondary option:** router-hosted VPN retained as a possible break-glass/recovery path

## Goal

Provide secure remote administrative access to the homelab without publishing management interfaces such as Proxmox, Grafana, SSH or internal web services directly to the Internet.

The normal operating model will be:

```text
Remote client
    |
    | WireGuard / UDP 51820
    v
ASUS RT-AC86U / WAN edge
    |
    | single UDP port-forward
    v
vpn-01
    |
    +----> 192.168.2.0/24 internal services
```

The VPN is an administration path, not a mechanism for making internal services public.

## Design decision

Use a dedicated VM as the primary VPN endpoint rather than making the router the everyday VPN server.

Reasons:

- keeps remote-access policy separate from the router's DHCP, DNS-advertisement, Wi-Fi and AiMesh roles;
- allows configuration to be managed and reviewed through the existing Git/IaC model;
- provides normal Linux firewalling, logging, patching and monitoring;
- permits WireGuard peer lifecycle to be managed independently of router firmware changes;
- makes backup and recovery consistent with other Proxmox workloads;
- avoids tying routine remote access to a future router factory-reset/rebuild.

The router remains attractive as an optional emergency path because it can remain available when the Proxmox guest hosting `vpn-01` is unavailable. That should be treated as a separate phase after the primary service is proven, using separate keys and a deliberately restricted policy.

## Proposed service identity

The following values are proposed and must be collision-checked immediately before provisioning:

| Item | Proposed value |
|---|---|
| Hostname | `vpn-01` |
| Platform | Debian minimal VM on Proxmox |
| Proposed VMID | `203` |
| Proposed LAN address | `192.168.2.57/24` |
| Gateway | `192.168.2.1` |
| VPN subnet | `10.44.0.0/24` |
| VPN server address | `10.44.0.1/24` |
| WireGuard port | `51820/udp` |
| Initial mode | split tunnel |
| Internal DNS | `192.168.2.51`, `192.168.2.50` |

`192.168.2.57` and VMID `203` are reservations in this design only until preflight proves they are unused in live DHCP, ARP, Proxmox inventory, DNS and Git-managed inventory.

## VM sizing

WireGuard has very small resource requirements for this estate.

Initial allocation:

```text
vCPU:       1
RAM:        512 MiB to 1 GiB
Disk:       8 GiB
NIC:        virtio, management LAN bridge
OS:         current approved Debian minimal build
Autostart:  enabled
```

Prefer the existing standard VM template/base-build path rather than introducing a special manual OS build.

Initial node placement should be selected during preflight after checking current resource headroom and recovery dependencies. The service must not be described as highly available while its disk remains node-local.

## WireGuard addressing and client model

Use one peer/key pair per device. Never share a private key between devices.

Suggested allocation model:

```text
10.44.0.1      vpn-01
10.44.0.10+    individually assigned remote clients
```

Each peer record should have a human-readable device identity in the protected operational inventory, for example:

```text
James-Laptop
James-Phone
Recovery-Laptop
```

Private keys and complete client configuration files must not be committed to Git.

Revocation is performed by removing the affected public-key peer from `vpn-01`, applying the configuration and recording the change.

## Routing design

### Preferred design: routed VPN subnet

Prefer proper routing so internal systems can retain the real VPN client address (`10.44.0.x`) in logs.

Required path:

```text
192.168.2.0/24 -> route 10.44.0.0/24 via 192.168.2.57
```

During implementation, verify whether the live ASUS firmware can provide the required static route cleanly and whether that route survives reboot/configuration export.

### Fallback design: NAT on vpn-01

If the router cannot support the required static route reliably, use `nftables` masquerading on `vpn-01` for traffic from `10.44.0.0/24` to the LAN.

This is operationally simpler but reduces per-client attribution on destination systems because connections may appear to originate from `vpn-01`.

The chosen mode must be documented after live validation. Do not leave both methods enabled accidentally.

## Split-tunnel policy

The initial service should not become a general Internet egress VPN.

Remote clients should route only the networks required to administer the homelab, initially:

```text
10.44.0.0/24
192.168.2.0/24
```

This reduces unnecessary dependency on the home WAN connection and keeps the purpose of the service clear.

A future full-tunnel profile may be added only if there is a deliberate requirement.

## Access-control policy

Do not treat VPN connectivity as unrestricted trust.

Initial policy should permit the VPN subnet to reach only required management/service destinations. Expected examples include:

- `admin-01` SSH;
- Proxmox management on `192.168.2.70` and `192.168.2.71`;
- Grafana/monitoring on `monitor-01`;
- Pi-hole/Unbound DNS services;
- selected internal application interfaces where remote administration is justified.

The initial rule set should deny traffic not explicitly required. Access can be widened after evidence shows a genuine operational need.

Administrative SSH to `vpn-01` itself should be permitted from the trusted LAN/admin path rather than exposed directly from the WAN.

## Router/WAN changes

The router should expose only the WireGuard listener required by the VM:

```text
WAN UDP/51820 -> 192.168.2.57 UDP/51820
```

No Proxmox, SSH, Grafana, Pi-hole or other management port should be forwarded to the Internet as part of this project.

If the WAN address is dynamic, use the approved DDNS mechanism and keep the client endpoint name separate from private-key material.

The future ASUS clean-rebuild plan must preserve or deliberately recreate the required WireGuard port-forward/DDNS settings after this project becomes operational.

## Host firewall

Use `nftables` on `vpn-01` with a default-deny policy.

At minimum:

- allow established/related traffic;
- allow SSH administration only from approved internal management sources;
- allow WireGuard UDP/51820 from the WAN-forwarded path;
- allow forwarding from the WireGuard interface only to approved internal destinations/services;
- deny unrelated forwarding;
- enable NAT only if the fallback routing design is selected.

Firewall configuration should be deployed through IaC once the live rule set has been validated.

## DNS

VPN clients may use the existing internal resolver pair:

```text
192.168.2.51  dns-01
192.168.2.50  dns-02
```

Validate both resolvers through the VPN path before making internal DNS the default in distributed client profiles.

Do not reintroduce retired resolver addresses.

## Monitoring and logging

`vpn-01` should follow the standard managed-host observability model.

Required minimum:

- host availability and resource metrics in Prometheus;
- Grafana Alloy/system journal shipping to Loki;
- WireGuard service health;
- interface state;
- configured peer count;
- latest-handshake age where useful;
- authentication/configuration/firewall errors;
- disk and package/update state through normal host monitoring.

Avoid high-noise per-packet logging.

A useful alert is service unavailable or no expected listener after boot. Individual peer inactivity should not normally page or alert.

## Security controls

- use modern WireGuard keys generated on trusted systems;
- one key pair per client;
- never store private keys, QR codes or full client configuration in Git;
- remove lost/retired device peers promptly;
- keep the VM patched through the normal lifecycle-management process;
- expose only UDP/51820 from the WAN;
- retain normal SSH key-based administration;
- do not enable password SSH from the Internet;
- use a default-deny host firewall;
- log configuration/service failures without logging secret material;
- review active peers periodically;
- maintain a documented key-rotation and peer-revocation procedure.

## Backup and recovery

After provisioning, add `vpn-01` to the appropriate Proxmox backup policy for its hosting node.

The VM backup is useful for rapid service recovery, but it must not be the only recovery route. Keep sufficient protected recovery material outside the VM to rebuild the service if the guest or Proxmox node is lost.

Recovery documentation must identify:

- the WireGuard subnet and endpoint port;
- current hosting node and VMID;
- router port-forward/DDNS dependency;
- firewall/routing mode;
- method for restoring or rotating server identity;
- process for regenerating client profiles if keys are intentionally rotated;
- validation steps from an external network.

Do not store recovery private keys in plaintext Git.

## Optional phase 2: router break-glass VPN

After `vpn-01` is stable, decide whether a second, router-hosted VPN endpoint is justified as an emergency access mechanism.

If implemented:

- use a separate listener/port from `vpn-01`;
- use separate server and client keys;
- restrict it to essential management access;
- do not use it as the normal day-to-day path;
- document and test it from outside the LAN;
- preserve it explicitly through any future router rebuild;
- review whether the extra Internet-facing service is worth the resilience benefit.

The router fallback is optional. The primary project is complete without it if the accepted recovery model is local access plus Proxmox/VM recovery.

# Project plan

## Phase 0 — preflight and design validation

**Estimated effort:** 30–60 minutes

Tasks:

- confirm `192.168.2.57` is unused in DHCP reservations, active leases, ARP/network-host inventory and DNS;
- confirm VMID `203` is unused cluster-wide;
- confirm current Proxmox node capacity and choose initial placement;
- confirm the standard Debian template/base-build path;
- record current router firmware and WAN/DDNS state;
- verify whether the router can provide a persistent static route to `10.44.0.0/24`;
- capture current firewall/port-forward state before changing it;
- choose the first two test peers, normally laptop and phone.

**Exit gate:** addressing, VMID, node placement and routing method are explicitly approved with no collision.

## Phase 1 — provision vpn-01

**Estimated effort:** 45–60 minutes

Tasks:

- provision the VM from the approved template;
- configure hostname, reserved LAN address and DNS;
- patch the OS;
- apply the normal SSH/admin baseline;
- deploy host monitoring/logging baseline;
- enable IP forwarding;
- install WireGuard and `nftables` configuration;
- enable service autostart.

**Exit gate:** VM survives reboot, is reachable from the management LAN and has normal monitoring/logging.

## Phase 2 — configure WireGuard and routing

**Estimated effort:** 60–90 minutes

Tasks:

- generate the server key securely;
- configure `wg0` as `10.44.0.1/24`;
- add individually identified test peers;
- implement preferred static routing or documented NAT fallback;
- implement default-deny forwarding policy;
- verify LAN-side connectivity before opening the WAN port.

**Exit gate:** a test peer on a controlled local/test path can reach only the intended internal destinations.

## Phase 3 — WAN cutover

**Estimated effort:** 30–60 minutes

Tasks:

- create UDP/51820 port-forward to `192.168.2.57`;
- configure/validate DDNS endpoint if required;
- verify the UDP listener from outside the home network;
- test using mobile data or another genuinely external connection;
- prove access to `admin-01`, both Proxmox nodes and monitoring as permitted;
- confirm unrelated internal destinations remain blocked if outside policy.

**Exit gate:** remote access works from an external network without exposing any additional management service directly to the Internet.

## Phase 4 — observability, backup and recovery

**Estimated effort:** 60–90 minutes

Tasks:

- add WireGuard-specific service/listener health telemetry;
- confirm logs arrive in Loki;
- add `vpn-01` to the correct Proxmox backup schedule;
- take and validate the first backup;
- write the operational/recovery runbook;
- document peer add/remove/rotate procedure;
- perform reboot testing for the VM and router path;
- record the final routing method and firewall policy in Git.

**Exit gate:** monitoring, backup, reboot persistence and recovery documentation are proven.

## Phase 5 — optional resilience decision

**Estimated effort:** 30–90 minutes, only if required

Decide whether the router-hosted break-glass VPN is worth deploying.

If yes, implement and test it as a separate restricted recovery service. If no, document the accepted recovery path and close the decision explicitly.

# Expected timeline

The primary `vpn-01` implementation is expected to be approximately **5–7 hours of hands-on work**, allowing it to be completed as one controlled working-day project without rushing validation.

A later router break-glass endpoint would be a separate small change.

# Acceptance criteria

The primary VPN project is complete only when all of the following are true:

- `vpn-01` identity, address, VMID and hosting node are recorded in Git;
- WireGuard starts automatically after reboot;
- at least two individually keyed clients have been tested;
- external connectivity has been proven from outside the LAN;
- no internal management web/SSH port has been exposed directly to the Internet;
- access control is narrower than unrestricted LAN trust;
- both internal DNS resolvers work through the VPN if configured for clients;
- monitoring and logs are visible on `monitor-01`;
- first Proxmox backup has succeeded and been validated;
- peer revocation has been tested or demonstrably validated;
- routing/NAT mode is explicitly documented;
- secrets/private keys are absent from Git;
- an operational/recovery runbook exists;
- the router break-glass decision is recorded as implemented or intentionally deferred.

# Rollback

If the WAN cutover produces unexpected behaviour:

1. remove/disable the router UDP/51820 port-forward;
2. disable the WireGuard interface/service on `vpn-01` if necessary;
3. remove any new static route or NAT rule associated with `10.44.0.0/24`;
4. confirm normal LAN, DNS, WAN and router operation is unchanged;
5. retain the VM and logs for diagnosis rather than immediately destroying evidence.

The project must not require rollback of unrelated router, DNS, Proxmox or switch configuration.

# IaC/documentation outputs

Expected repository outputs during implementation:

- inventory entry for `vpn-01`;
- VM provisioning definition using the approved Proxmox/IaC path;
- WireGuard package/service role or equivalent reviewed configuration;
- `nftables` policy under managed configuration;
- monitoring/logging integration;
- backup-policy update;
- production service document after go-live;
- operational/recovery runbook and runbook-registry entry;
- final update to `CURRENT-STATE.md` only after the service is proven operational.

Until those acceptance gates are complete, this document remains a target design and project plan rather than evidence that the VPN is live.
