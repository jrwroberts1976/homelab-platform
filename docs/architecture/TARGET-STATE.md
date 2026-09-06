# Target-State Architecture

This is a working design, not yet approved as final.

## Working direction

- Public portfolio website: external static hosting where possible.
- Proxmox: primary compute platform.
- `docker-core-01`: proposed general persistent Docker VM.
- `monitoring-01`: proposed monitoring VM.
- `ids-01`: security-focused host.
- Raspberry Pis: edge, appliance, location-dependent, test or lightweight roles.
- Komodo Core: proposed on primary x86 Docker infrastructure, not TestServer.
- Komodo Periphery: only on approved Docker hosts.
- Renovate: hosted GitHub App with repository configuration in Git.
- Jenkins / Stage 6: retire after replacement deployment path is proven.

## Host-owned IaC direction

Future repository structure should make deployment ownership explicit, for example:

```text
hosts/
├── docker-core-01/
├── monitoring-01/
├── ids-01/
├── testserver/
├── birdnet-01/
└── pihole-*/
```

Shared roles, modules and policy may be reused, but a deployable workload must have an explicit target host.
