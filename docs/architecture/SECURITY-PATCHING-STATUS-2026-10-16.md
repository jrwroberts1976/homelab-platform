<!-- estate-authority: IaC/inventory/estate.json -->
# Security, Patching and Vulnerability Status — 16 October 2026

**Status:** CURRENT DAY-END RECONCILIATION / FINAL GREENBONE SCAN PENDING  
**Authoritative current-state:** `docs/architecture/CURRENT-STATE.md`  
**Planning authority:** `docs/architecture/ACTIVE-INFRASTRUCTURE-BACKLOG.md`

This record captures the 16 October 2026 maintenance and hardening work so the current state can be recovered without relying on conversation history.

## Estate patching

A controlled full patch session completed across the 15 Ansible-managed Linux hosts.

Final validated state:

```text
hosts reachable: 15 / 15
pending updates: 0
reboot required: 0
```

Service validation found no patch-induced production regression. Both Proxmox nodes remained quorate with QDevice present. Patch telemetry was refreshed across the full managed baseline.

### Proxmox repository correction

The active Ceph enterprise repository was discovered on `PROXMOX` even though Ceph is not configured/in use. The repository is now explicitly disabled through the `proxmox_repositories` Ansible role.

Current rebased commit recorded during the session:

```text
9dc60394 fix(proxmox): disable unused Ceph enterprise repository
```

## Trusted HTTPS rollout

Trusted Let's Encrypt HTTPS is implemented for:

```text
dns-01.home.jrwroberts.co.uk
dns-02.home.jrwroberts.co.uk
greenbone.home.jrwroberts.co.uk
grafana.home.jrwroberts.co.uk
zabbix.home.jrwroberts.co.uk
proxmox.home.jrwroberts.co.uk
proxmox-2.home.jrwroberts.co.uk
```

Certificate issuance/renewal uses Cloudflare DNS validation. Service-specific deploy hooks were validated through Certbot dry-runs on every endpoint.

Post-renewal checks remained healthy:

- Pi-hole: FTL active and combined PEM valid;
- Greenbone: nginx container healthy and HTTPS 200;
- Grafana: nginx healthy, trusted HTTPS 302, backend bound only to `127.0.0.1:3000`;
- Zabbix: nginx healthy and HTTPS 200;
- both Proxmox nodes: `pveproxy` active, trusted HTTPS 200 and quorum intact.

Grafana HTTPS implementation is present on `main` as:

```text
bb5aecd9 feat(tls): add trusted HTTPS for Grafana
```

The Cloudflare Python 2.20.x warning emitted during Certbot DNS testing is non-fatal. Dependency version control remains follow-up technical debt.

## Accepted-risk reporting

Accepted risks remain separate from actionable findings. The repository now contains the accepted-risk detail publication/export/dashboard work rather than exposing only an aggregate count.

Recent main-branch commits observed on 16 October include:

```text
62ec87ba feat(greenbone): publish accepted risk finding details
572c27d2 feat(monitoring): export accepted risk details
82326d3f feat(grafana): add accepted risk details panel
```

## Raspberry Pi TF-A mitigation

`docker-01` is:

```text
Raspberry Pi 4 Model B Rev 1.5
Revision: c03115
Architecture: aarch64
OS: Debian 13
```

Trusted Firmware-A v2.15.0 release firmware is active with validated SHA-256:

```text
b1d31e5094c692b41ee9418a20216176bd1c2764f27e18a5fdc4d6187a307405
```

Live kernel evidence:

```text
Spectre v2: Mitigation: Branch predictor hardening, BHB
Speculative Store Bypass: Not affected
```

The change is now reproducible IaC through `roles/raspberry_pi_tfa_hardening`. The role vendors the validated artifact and records its checksum, licence and provenance; validates host/model/revision/architecture; uses a FAT-safe boot-config backup; manages only its own TF-A boot block; and does not automatically reboot.

A second real playbook run completed idempotently with:

```text
changed=0
failed=0
```

Current main-branch commit:

```text
b3047742 feat(security): manage Raspberry Pi TF-A mitigation
```

## Greenbone validation status

The last fully reviewed managed scan before today's remediation had:

```text
Critical:      0
High:          0
Medium:        1 actionable
Low:           0
Accepted risk: 30
```

The actionable Medium was the Zabbix cleartext HTTP management finding. Trusted Zabbix HTTPS/reverse-proxy remediation is now implemented.

A final post-remediation Greenbone scan is **running/pending completion**. This is the remaining closure gate.

When the scan completes, review and record:

1. Critical/High/Medium/Low counts.
2. Accepted-risk count and detail reconciliation.
3. Whether the prior Zabbix cleartext finding is absent.
4. Whether the prior Raspberry Pi speculative-execution findings are absent/reconciled after TF-A.
5. Any new actionable finding introduced since the previous report.

Until that review is complete, describe **patching as complete** and **vulnerability remediation as awaiting final scan validation**.

## Remaining security / technical debt

- encode the already-proven Proxmox `gather_data_sampling=force` mitigation in IaC;
- deliberately manage the Certbot Cloudflare Python dependency before a future incompatible 3.x migration;
- complete the final Greenbone scan review;
- continue Project 7 estate-wide container image lifecycle work when reprioritised;
- complete Backup/DR recovery-depth work.

## Next user-selected investigation

After the final Greenbone scan is reviewed, the next requested investigation is **Raspberry Pi overclocking feasibility**.

This should begin read-only. Capture Pi model/revision, cooling, power supply, current clock/governor behaviour, temperatures, throttle/undervoltage history and workload benefit before proposing any clock or voltage change. `docker-01` TF-A/security boot requirements must remain intact.
