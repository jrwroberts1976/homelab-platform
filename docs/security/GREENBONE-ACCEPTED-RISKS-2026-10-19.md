<!-- estate-authority: IaC/inventory/estate.json -->

# Greenbone accepted-risk assessment — 19 October 2026

**Status:** Review only. No accepted-risk policy or live firewall changes, and no new Greenbone scan completed by this review.

## Last report's 15 accepted findings

| Finding | NVT OID | Count | Disposition |
| --- | --- | ---: | --- |
| ICMP Timestamp Reply Information Disclosure | 1.3.6.1.4.1.25623.1.0.103190 | 14 | Candidate for narrow IPv4 ICMP timestamp-request (type 13) filtering, once firewall owner is identified |
| BirdNET-Go csrf cookie missing HttpOnly | 1.3.6.1.4.1.25623.1.0.105925 | 1 | Keep accepted pending deployed-version CSRF compatibility verification |

The accepted-risk **allowlist** also contains 15 older TCP timestamp NVT 1.3.6.1.4.1.25623.1.0.80091 entries; these are not among the 15 findings in the last report. Do not indiscriminately turn off TCP timestamps.

## Host scope for ICMP timestamp review

| Host | IPv4 | Special considerations |
| --- | --- | --- |
| media-01 | 192.168.2.195 | First pilot candidate: Git-managed nftables input currently broadly accepts ICMP; protect Kodi, SMB, NFS, HTTPS |
| docker-01 | 192.168.2.220 | Docker/BirdNET networking |
| admin-01 | 192.168.2.48 | SSH, Ansible controller, QNetd |
| dns-02 | 192.168.2.50 | Pi-hole/Unbound LXC |
| dns-01 | 192.168.2.51 | Pi-hole/Unbound LXC |
| monitor-01 | 192.168.2.52 | Grafana/monitoring |
| cloud-01 | 192.168.2.53 | Nextcloud |
| mail-relay-01 | 192.168.2.54 | SMTP relay |
| sensor-01 | 192.168.2.55 | Network sensor |
| edge-01 | 192.168.2.56 | LXC policy |
| greenbone-01 | 192.168.2.57 | Scanning and Docker |
| komodo-01 | 192.168.2.58 | Container control plane |
| zabbix-01 | 192.168.2.59 | Monitoring |
| Proxmox-2 | 192.168.2.71 | Hypervisor: Proxmox-native firewall/cluster safety |

PROXMOX at 192.168.2.70 is NOT in the last report's 14 ICMP findings. Its older TCP timestamp acceptance is a separate category.

## Recommended mitigation strategy

For a confirmed nftables-managed input chain, an IPv4 ICMP type 13 request drop before a broad IPv4 ICMP allow is promising. Do not drop all ICMP: preserve echo/ping, path MTU and IPv6 network/neighbor discovery. Some hosts may use Proxmox-native filtering, UFW or Docker-managed rules; these must be diagnosed separately. Never introduce an unmanaged temporary host firewall rule as the persistent fix.

The BirdNET-Go csrf cookie is intentionally not HttpOnly in upstream middleware, and is different from a login-session cookie. The frontend in newer source also retrieves its token from /api/v2/app/config, which does NOT prove that every deployed code path tolerates an HttpOnly override. The Nginx Secure flag has already been corrected. Do not set HttpOnly without testing the exact installed version and state-changing WebUI actions.

## Execution plan

1. Run the new read-only Ansible playbook IaC/ansible/playbooks/greenbone-accepted-icmp-firewall-readonly.yml on the 14 affected hosts after syntax checking. Only non-secret firewall indicators and rule-reference counts are printed.
2. Use results to choose a single pilot, likely media-01; stage a Git-managed narrow ICMP filter with rollback and non-disruptive validation.
3. Expand only with mechanism-specific code where each host's firewall owner is known; treat the hypervisor and containers with particular care.
4. Obtain a fresh completed authenticated Greenbone report. Only remove corresponding accepted-risk entries after scanner evidence confirms they no longer occur.
5. Leave the BirdNET HttpOnly exception accepted unless compatible CSRF behaviour is demonstrated on the running version.

**No mitigation has been deployed and no risk status has been changed by this review.**
