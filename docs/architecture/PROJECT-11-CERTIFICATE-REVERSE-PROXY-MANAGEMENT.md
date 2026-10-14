# Project 11 — Certificate & Reverse Proxy Management

<!-- estate-authority: IaC/inventory/estate.json -->

**Status:** PLANNED  
**Priority:** Start after the current Greenbone validation/remediation work is closed.  
**Preferred candidate:** Nginx Proxy Manager (NPM), subject to design validation before deployment.  
**Purpose:** Replace ad-hoc browser-facing self-signed certificates with a centrally managed, renewable TLS and reverse-proxy design while preserving separate service-to-service trust where appropriate.

## Why this project exists

The estate now has multiple internal web services that use HTTP, self-signed certificates, or individually managed TLS. That creates avoidable browser warnings, inconsistent renewal processes, and duplicated certificate-management work.

The current Greenbone finding for cleartext Zabbix HTTP traffic also demonstrates that certificate and reverse-proxy management should be solved as an estate capability rather than as a one-off Zabbix fix.

## Design principles

1. Separate **browser-facing HTTPS** from **service-to-service TLS**.
2. Prefer centrally managed, automatically renewable certificates for browser-facing services.
3. Do not replace an internal CA or direct service-to-service trust merely to force everything through a reverse proxy.
4. Do not expose internal services publicly unless separately and explicitly approved.
5. Prefer DNS-01 certificate validation so internal services can receive trusted certificates without inbound Internet exposure.
6. Use least-privilege credentials for DNS automation.
7. Keep the reverse proxy recoverable from Git/IaC plus backed-up runtime state.
8. Migrate one service at a time and retain a tested rollback path.

## Candidate architecture

The preferred design to validate is:

```text
Client browser
    |
    | HTTPS using a publicly trusted certificate
    v
+-----------------------------+
| proxy-01                    |
| Nginx Proxy Manager         |
| TLS termination / routing   |
+-----------------------------+
    |       |       |       |
    |       |       |       +--> Greenbone / other approved web UIs
    |       |       +----------> Komodo
    |       +------------------> Grafana
    +--------------------------> Zabbix
```

Internal DNS would resolve approved service names to `proxy-01`. Certificate issuance should use Cloudflare DNS-01 validation with a narrowly scoped API token.

Example naming pattern to validate:

```text
grafana.home.jrwroberts.co.uk
zabbix.home.jrwroberts.co.uk
komodo.home.jrwroberts.co.uk
greenbone.home.jrwroberts.co.uk
birdnet.home.jrwroberts.co.uk
```

Names are provisional until the DNS and naming design is reviewed.

## Scope

### 1. Certificate inventory

Inventory all current certificates and browser-facing HTTP/HTTPS endpoints, including:

- hostname / service;
- listening port;
- HTTP versus HTTPS;
- certificate issuer;
- self-signed versus trusted;
- expiry date;
- renewal mechanism;
- current DNS name;
- whether the certificate is browser-facing or service-to-service;
- whether the endpoint is already behind Cloudflare or another proxy.

### 2. Trust classification

Classify every TLS relationship as one of:

- browser-facing HTTPS suitable for reverse-proxy termination;
- direct service-to-service TLS that should retain explicit CA validation;
- internal API traffic that should move to HTTPS but may not belong behind NPM;
- legacy/self-signed TLS that can be retired after migration.

The existing CA-validated Komodo Core ↔ Periphery WSS trust must not be replaced automatically. It should be reviewed separately as service-to-service TLS.

### 3. NPM design validation

Validate Nginx Proxy Manager as the preferred reverse-proxy platform, including:

- supported current release and upgrade strategy;
- pinned image/version rather than `latest`;
- Docker/Compose deployment model;
- host sizing and placement;
- whether a dedicated `proxy-01` host is justified;
- NPM administrative access restrictions;
- data/database persistence;
- compatibility with WebSockets and long-lived application connections;
- certificate issuance and renewal behaviour;
- rollback path.

If NPM cannot meet the requirements cleanly, compare alternatives before deployment rather than forcing the design.

### 4. DNS and ACME

Design and implement:

- internal DNS records through the authoritative internal DNS/Pi-hole path;
- Cloudflare DNS-01 ACME validation;
- a least-privilege Cloudflare API token restricted to the required zone and DNS operations;
- no dependency on inbound public HTTP/HTTPS exposure for certificate issuance;
- documented DNS and certificate renewal flow.

### 5. Proxy host deployment

Deploy the selected reverse proxy through IaC with:

- pinned versions;
- persistent storage;
- health checks;
- controlled administrative exposure;
- monitoring;
- logging;
- backup and restore coverage;
- documented update procedure.

If `proxy-01` is created, add it to the canonical inventory and monitoring stack only after the deployment design is approved.

### 6. Service migration

Migrate services individually rather than in a single cutover.

Suggested initial order:

1. **Zabbix** — highest immediate security value because current management/API access is plain HTTP on port 8080.
2. **Grafana** — straightforward browser-facing service and useful validation target.
3. **Komodo web UI/API** — validate WebSocket behaviour carefully; do not disturb Periphery trust.
4. **Greenbone web UI** — migrate only after the current Greenbone validation work is complete.
5. **BirdNET-Go and other suitable internal web applications** — migrate only where a reverse proxy adds clear value.

For each service:

- create internal DNS record;
- create proxy host;
- obtain trusted certificate;
- validate HTTP→HTTPS behaviour;
- validate application login/session/WebSocket behaviour;
- validate monitoring and automation clients;
- update documentation and bookmarks/API endpoints where appropriate;
- retain direct backend access until rollback confidence is established;
- remove obsolete direct/self-signed exposure only after validation.

### 7. Certificate lifecycle monitoring

Add operational visibility for:

- certificate expiry date;
- certificate renewal failures;
- proxy health;
- backend reachability;
- DNS/ACME failures;
- reverse-proxy container/service health.

Certificate expiry should become a monitored condition rather than a manual calendar task.

### 8. Backup and recovery

Protect all state required to recover the proxy and certificate service, including at minimum:

- NPM `/data`;
- NPM `/etc/letsencrypt`;
- database state if an external database is selected;
- IaC/Compose configuration;
- DNS design and recovery documentation;
- secret/token recovery procedure without committing secrets to Git.

Perform at least one recovery test before closing the project.

## Explicit non-goals

- No automatic public exposure of internal applications.
- No blanket replacement of all internal CA certificates.
- No removal of service-to-service TLS validation merely because NPM exists.
- No wildcard administrative permissions for the Cloudflare API token when narrower permissions are possible.
- No unmanaged `latest` container tags.
- No mass cutover of all services at once.

## Initial implementation sequence

1. Complete the active Greenbone validation/remediation work.
2. Inventory current web endpoints and certificates.
3. Classify browser-facing versus service-to-service TLS.
4. Decide the `proxy-01` placement and resource model.
5. Validate NPM against required features and current application behaviours.
6. Design internal DNS and Cloudflare DNS-01 permissions.
7. Deploy NPM through IaC with pinned versions and backup coverage.
8. Migrate Zabbix first and verify that trusted HTTPS removes the cleartext management path.
9. Migrate Grafana as the second validation service.
10. Migrate remaining approved browser-facing services one at a time.
11. Add certificate-expiry and proxy-health monitoring.
12. Perform backup/restore validation.
13. Update `CURRENT-STATE.md`, estate inventory and service documentation only after live validation.

## Completion criteria

Project 11 is complete only when all of the following are true:

- the current certificate/endpoints inventory is documented;
- browser-facing and service-to-service TLS are explicitly classified;
- the reverse-proxy platform and host placement are documented and reproducible through IaC;
- trusted certificates are issued using an automated renewal path;
- DNS-01 works without exposing the target applications publicly;
- Cloudflare credentials use least privilege;
- Zabbix browser/API access has a validated HTTPS path;
- at least one additional production service is migrated successfully;
- WebSocket/session-dependent services are tested where applicable;
- certificate expiry and proxy health are monitored;
- backup and recovery of proxy/certificate state are proven;
- no required secret is committed to Git;
- obsolete self-signed/browser-facing certificate paths are removed only after replacement validation;
- canonical documentation is updated to reflect the final live design.

## Current status

**PLANNED.** No NPM deployment or `proxy-01` host is claimed yet. The immediate active work remains the Greenbone validation scan and vulnerability remediation already in progress on 14 October 2026.
