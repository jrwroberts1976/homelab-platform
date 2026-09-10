# Cloudflare Edge Service

**Authority:** `jrwroberts1976/homelab-platform`
**Host:** `edge-01.jameshouse` / `192.168.2.56`
**Placement:** LXC CT103 on `Proxmox-2` (`192.168.2.71`)
**Status:** base host operational; `cloudflared`, tunnel and Access policies pending

## Purpose

`edge-01` is the dedicated outbound Cloudflare connector for selected internal web applications. It isolates public ingress from application hosts and replaces the long-term need for Nginx Proxy Manager/Authelia as the external access boundary.

## Approved architecture

```text
Internet
   |
   v
Cloudflare Zero Trust / Access
   |
   v
Cloudflare Tunnel
   |
   v
edge-01 192.168.2.56
   |
   +--> selected internal services only
```

No inbound router port-forward is required for the tunnel.

## Base host

Validated 10 September 2026:

- Debian 13 (trixie)
- unprivileged LXC
- CT ID 103
- 1 vCPU
- 768 MiB RAM
- 256 MiB swap
- 8 GiB root disk
- static IPv4 `192.168.2.56/24`
- gateway `192.168.2.1`
- DNS `192.168.2.51`, `192.168.2.50`
- search domain `jameshouse`
- starts automatically with `Proxmox-2`
- `nesting=1` enabled for Debian 13/systemd mount behaviour
- `/tmp` tmpfs capped at 192 MiB
- systemd state `running`, zero failed units
- SSH host fingerprint verified before trust
- root SSH uses the `proxmox-automation` identity from `admin-01`
- outbound HTTPS to Cloudflare validated
- outbound TCP/7844 to Cloudflare tunnel infrastructure validated

## Security rules

- Keep the container unprivileged.
- Do not install Docker merely to run `cloudflared`; use the native service/package unless a separate design change approves otherwise.
- Tunnel credentials/tokens are secrets and must never be committed or echoed into documentation/logs.
- Public hostnames are explicit allowlisted routes; do not create a wildcard route by default.
- Cloudflare Access protects administrative applications before they are considered externally usable.
- Prefer passkeys/security keys/strong MFA for interactive administration with TOTP fallback.
- Machine/API traffic should use service authentication rather than interactive MFA.
- Do not expose SSH itself through the public application tunnel unless a separate reviewed requirement exists.

## Implementation sequence

1. install `cloudflared` from a controlled/verified package source;
2. verify package version and systemd unit;
3. create the tunnel in Cloudflare;
4. install connector credentials outside Git;
5. start the connector and confirm healthy outbound tunnel sessions;
6. add one low-risk test hostname/service route;
7. apply Cloudflare Access policy before exposing an administrative service;
8. test unauthenticated denial, successful MFA and application reachability;
9. add monitoring for connector service state/tunnel health;
10. document each production hostname and its internal origin;
11. repeat only for explicitly approved services.

## Validation

Minimum validation after installation/change:

```bash
ssh edge-01 'systemctl is-active cloudflared'
ssh edge-01 'systemctl --failed --no-pager'
ssh edge-01 'journalctl -u cloudflared -n 50 --no-pager'
```

Also prove through Cloudflare that:

- the tunnel reports connected/healthy;
- the expected hostname is routed through the expected tunnel;
- Access blocks a browser without valid authentication;
- valid MFA reaches only the intended origin;
- no router inbound port-forward was introduced as part of the change.

## Recovery

If the connector fails:

1. confirm `edge-01` itself is reachable on the LAN;
2. confirm DNS/default route and outbound HTTPS/7844 connectivity;
3. inspect `cloudflared` service status/journal without exposing credentials;
4. verify the Cloudflare tunnel/connector state;
5. restart only the connector service if configuration is known-good;
6. reinstall/re-register from documented secret material if the connector state is unrecoverable;
7. keep internal LAN access available even when Cloudflare ingress is down.

A broken tunnel must not be worked around by opening ad-hoc router ports.

## Monitoring

Pending until `cloudflared` is installed. At minimum monitor:

- host reachability;
- host resource pressure;
- `cloudflared` systemd state;
- tunnel health/connection state where a reliable metric/source is available;
- externally protected application availability without bypassing Access policy.

## Definition of done

The edge service is operational only when `cloudflared` is installed, the tunnel is healthy, at least one approved service is published through an Access policy, authentication is proven, monitoring exists, and recovery steps have been exercised or validated.
