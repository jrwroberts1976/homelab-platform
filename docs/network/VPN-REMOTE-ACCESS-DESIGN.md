<!-- estate-authority: IaC/inventory/estate.json -->
# VPN Remote-Access Design and Project Plan

**Status:** approved design / planned implementation; deployment identity not yet allocated  
**Reviewed:** 16 September 2026  
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

## Deployment identity

`vpn-01` remains the proposed service name, but its LAN address and VMID are deliberately **unallocated**.

The address and VMID previously proposed for this design are now occupied by the live `greenbone-01` scanner. They must not be reused for the VPN.

Allocation happens only during deployment preflight, after checking the canonical estate inventory and live Proxmox/network state.

| Item | Current design value |
|---|---|
| Hostname | `vpn-01` (proposed) |
| Platform | Debian minimal VM on Proxmox |
| VMID | unallocated; assign during deployment preflight |
| LAN address | unallocated; assign during deployment preflight |
| Preferred node | `Proxmox-2`, subject to live capacity/recovery review |
| Gateway | `192.168.2.1` |
| VPN subnet | `10.44.0.0/24` |
| VPN server address | `10.44.0.1/24` |
| WireGuard port | `51820/udp` |
| Initial mode | split tunnel |
| Internal DNS | `192.168.2.51`, `192.168.2.50` |

Do not add `vpn-01` to `IaC/inventory/estate.json` until a real LAN address has been selected and collision-checked. Do not invent a replacement address or VMID merely to keep this design numerically complete.

## VM sizing

WireGuard has small resource requirements for this estate.

Initial allocation target:

```text
vCPU:       1
RAM:        512 MiB to 1 GiB
Disk:       8 GiB
NIC:        virtio, management LAN bridge
OS:         current approved Debian minimal build
Autostart:  enabled
```

Prefer the existing standard VM template/base-build path rather than introducing a special manual OS build.

The service must not be described as highly available while its disk remains node-local.

## WireGuard addressing and client model

Use one peer/key pair per device. Never share a private key between devices.

Suggested VPN allocation model:

```text
10.44.0.1      vpn-01
10.44.0.10+    individually assigned remote clients
```

Each peer record should have a human-readable device identity in the protected operational inventory. Private keys and complete client configuration files must not be committed to Git.

Revocation is performed by removing the affected public-key peer from `vpn-01`, applying the configuration and recording the change.

## Routing design

### Preferred design: routed VPN subnet

Prefer proper routing so internal systems can retain the real VPN client address (`10.44.0.x`) in logs.

The implementation-time route will be:

```text
192.168.2.0/24 -> route 10.44.0.0/24 via <vpn-lan-ip>
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

A future full-tunnel profile may be added only if there is a deliberate requirement.

## Access-control policy

Do not treat VPN connectivity as unrestricted trust.

Initial policy should permit the VPN subnet to reach only required management/service destinations, such as:

- `admin-01` SSH;
- Proxmox management on `192.168.2.70` and `192.168.2.71`;
- Grafana/monitoring on `monitor-01`;
- Pi-hole/Unbound DNS services;
- selected internal application interfaces where remote administration is justified.

The initial rule set should deny traffic not explicitly required. Administrative SSH to `vpn-01` itself should be permitted from the trusted LAN/admin path rather than exposed directly from the WAN.

## Router/WAN changes

The router should expose only the WireGuard listener required by the VM:

```text
WAN UDP/51820 -> <vpn-lan-ip> UDP/51820
```

No Proxmox, SSH, Grafana, Pi-hole or other management port should be forwarded to the Internet as part of this project.

If the WAN address is dynamic, use the approved DDNS mechanism and keep the client endpoint name separate from private-key material.

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

Avoid high-noise per-packet logging. A useful alert is service unavailable or no expected listener after boot; individual peer inactivity should not normally page.

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

Recovery documentation must identify the allocated LAN address and VMID, VPN subnet and endpoint port, hosting node, router dependency, firewall/routing mode, server-identity recovery method and external validation steps.

Do not store recovery private keys in plaintext Git.

## Optional phase 2: router break-glass VPN

After `vpn-01` is stable, decide whether a second, router-hosted VPN endpoint is justified as an emergency access mechanism.

If implemented, use a separate listener/port and separate keys, restrict it to essential management access, test it from outside the LAN and preserve it explicitly through any future router rebuild.

The router fallback is optional. The primary project is complete without it if the accepted recovery model is local access plus Proxmox/VM recovery.

# Project plan

## Phase 0 — preflight and identity allocation

**Estimated effort:** 30–60 minutes

Tasks:

- read `IaC/inventory/estate.json` and `CURRENT-STATE.md`;
- choose a candidate unused LAN address without reusing any active/reserved address;
- confirm that address is unused in DHCP reservations, active leases, ARP/network-host inventory and DNS;
- choose an unused cluster-wide VMID;
- confirm current Proxmox node capacity and placement;
- confirm the standard Debian template/base-build path;
- record current router firmware and WAN/DDNS state;
- verify whether the router can provide a persistent static route to `10.44.0.0/24`;
- capture current firewall/port-forward state before changing it;
- update `IaC/inventory/estate.json` with the approved planned identity in the same change that starts implementation.

**Exit gate:** LAN address, VMID, node placement and routing method are explicitly approved with no collision.

## Phase 1 — provision vpn-01

**Estimated effort:** 45–60 minutes

- provision the VM from the approved template using the allocated identity;
- configure hostname, reserved LAN address and DNS;
- patch the OS and apply the normal SSH/admin baseline;
- deploy monitoring/logging;
- enable IP forwarding;
- install WireGuard and managed `nftables` configuration;
- enable service autostart.

**Exit gate:** VM survives reboot, is reachable from the management LAN and has normal monitoring/logging.

## Phase 2 — configure WireGuard and routing

**Estimated effort:** 60–90 minutes

- generate the server key securely;
- configure `wg0` as `10.44.0.1/24`;
- add individually identified test peers;
- implement preferred static routing or documented NAT fallback;
- implement default-deny forwarding policy;
- verify LAN-side connectivity before opening the WAN port.

**Exit gate:** a test peer on a controlled path can reach only the intended internal destinations.

## Phase 3 — WAN cutover

**Estimated effort:** 30–60 minutes

- create UDP/51820 port-forward to the allocated `vpn-01` LAN address;
- configure/validate DDNS endpoint if required;
- verify the listener from outside the home network;
- test using mobile data or another genuinely external connection;
- prove access to `admin-01`, both Proxmox nodes and monitoring as permitted;
- confirm unrelated destinations remain blocked if outside policy.

**Exit gate:** remote access works externally without exposing any additional management service directly to the Internet.

## Phase 4 — observability, backup and recovery

**Estimated effort:** 60–90 minutes

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

Decide whether the router-hosted break-glass VPN is worth deploying. If yes, implement and test it as a separate restricted recovery service. If no, document the accepted recovery path and close the decision explicitly.

# Expected timeline

The primary `vpn-01` implementation remains approximately **5–7 hours of hands-on work**, allowing one controlled working-day project without rushing validation. Identity allocation is part of phase 0, not a pre-existing reservation.

# Acceptance criteria

The primary VPN project is complete only when:

- `vpn-01` identity, allocated address, VMID and hosting node are recorded in Git;
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

If WAN cutover produces unexpected behaviour:

1. remove/disable the router UDP/51820 port-forward;
2. disable the WireGuard interface/service on `vpn-01` if necessary;
3. remove any new static route or NAT rule associated with `10.44.0.0/24`;
4. confirm normal LAN, DNS, WAN and router operation is unchanged;
5. retain the VM and logs for diagnosis rather than immediately destroying evidence.

The project must not require rollback of unrelated router, DNS, Proxmox or switch configuration.

# IaC/documentation outputs

Expected repository outputs during implementation:

- planned inventory entry for `vpn-01` once an address/VMID are genuinely allocated;
- VM provisioning definition using the approved Proxmox/IaC path;
- WireGuard package/service role or equivalent reviewed configuration;
- managed `nftables` policy;
- monitoring/logging integration;
- backup-policy update;
- production service document after go-live;
- operational/recovery runbook and runbook-registry entry;
- final update to `CURRENT-STATE.md` only after the service is proven operational.

Until those acceptance gates are complete, this document remains a target design and project plan rather than evidence that the VPN is live.
