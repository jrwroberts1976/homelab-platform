<!-- estate-authority: IaC/inventory/estate.json -->
# GitHub branch merge reconciliation — 29 October 2026

## Verified status

Scope: `jrwroberts1976/homelab-platform`, GitHub branches and PRs inspected on 29 October 2026.

- **53 branch refs** (including `main`). **52 other branches**: 42 associated with at least one **merged PR**, 6 only associated with an intentionally closed **unmerged PR**, and 4 without a PR history in the inspected repository listing.
- GitHub REST `pulls?state=open` returned **0 open PRs**. A branch remaining listed does **not** imply its PR is still open or its changes are absent from `main`.
- Final verified admin-01/QDevice recovery documentation PR **#238 merged** to main at commit `0f27cb3df590228259774ad7fa77f97d21aef731`, after `Estate and documentation guard` SUCCESS. This records both Proxmox nodes quorate, **3/3 total votes** with QDevice **one counted vote**, both QDevice clients `Connected`, and `admin-01` restored via router DHCP reservation to `192.168.2.48`. Recovery was fully independently verified without additional Proxmox/Corosync writes.

## Six deliberately closed unmerged PRs — DO NOT BULK MERGE

| Branch | PR | Disposition |
|---|---|---|
| `docs/handover-trivy-prometheus-confirmed-20261026` | #196 | Superseded by newer `main` Trivy/Prometheus five-host evidence; old handover prefix is historical, not latest instructions |
| `docs/security-remediation-programme-2026-10-20` | #188 | Superseded by merged reconciliation **#216**; do not overwrite newer security programme and estate backlog |
| `feature/pi-router-iac-birdnet-poc-migration-20261027` | #207 | Old `192.168.3.1`/Kea trial and cutover scripts not compatible with live `192.168.2.1`/dnsmasq; Docker/BirdNET retirement scripts could disrupt live services; supersession documented by merged **#222** |
| `feature/router-01-toolset-audit-20261028` | #210 | Obsolete `.3.1` assertions and broad package/SSH/network writers; a safe read-only monitoring path extracted through merged **#221**, earlier baseline **#211**, later separate monitoring changes; preserve history for independently reviewed extraction |
| `fix/router-01-pppoe-mss-persistence-20261028` | #208 | Old `.3.1`/subnet-controlled writer unsuitable today; live MSS persistent clamp independently verified by merged **#212** and evidence **#213** |
| `security/nextcloud-renewal-evidence` | #190 | Superseded by merged documentation **#215** after conflict resolution; never treat source evidence as a live certificate renewal |

The additional closed Grafana patch PR **#204** was also intentionally superseded by documentation PR **#217**; its older branch name `security/grafana-1324-patch-20261026` also has a separately merged PR **#202**, so is counted among the 42 branches with merged PRs. Do not infer any live Grafana deployment.

## Four branches without a PR in checked history

| Branch | Inspection | Action |
|---|---|---|
| `project3-closure-docs-20261010` | Ancestor of main: ahead 0, behind ~1059 at inspection | No merge work; historical branch |
| `project3-evidence-semantics` | Ancestor of main: ahead 0, behind ~1062 | No merge work; historical branch |
| `zabbix-monitoring-migration` | Ancestor of main: ahead 0, behind ~1103 | No merge work; historical branch |
| `backup/router-device-grafana-wip-20261011` | Unmerged old WIP containing network presence sweep, router Nmap worker, event role and dashboards, with many missing-from-main files and stale versions of existing monitoring assets | **Do not bulk merge**: separately assess whether still desired, dependencies, security/privacy, current architecture and tests; salvage a small reviewed feature PR only if required |

## Merged-PR branch heads are historical

The majority of `docs/*`, `feature/*`, `monitoring/*`, `security/*` and `merge/*` refs are kept after their PRs have already been squash-merged. Comparing an old head to `main` can show apparent `ahead` commits and conflicting old text because squash merge yields different SHAs. That alone is **not evidence of missing functional changes**.

A spot-check of router branches verified that:
- Former admin-01 reservation branch has the **five IaC/CI files matching main**; differences are obsolete pre-recovery documentation.
- Former router monitoring audit branch has the **two IaC/CI files matching main**; differences are old audit prose.
- Most other checked router heads also differ only by stale runbook/handover text; they should not overwrite the newer 29 Oct incident closure.
- Old broad toolset, Kea migration and MSS writers are exceptions with distinct unmerged files but explicit safety reasons not to transplant them wholesale.

## Merge decision and next actions

**Current safe merge queue: none after #238.** Do not merge already-merged PR branch heads again; do not reopen obsolete closed PRs or bypass their gates. Keep the historical refs for review; branch deletion or archive housekeeping is a **separate** decision and not authorised by this reconciliation.

For additional work, open a new narrow branch from latest main, recover only clearly valuable current-state features from historical WIP after an independent design review, add IaC validation, run CI, and require explicit approval for any router/firewall/DHCP/Proxmox/monitoring runtime deployment. Maintain `docs/architecture/CURRENT-STATE.md` and `gpt-handover.md` as the canonical current truth, with old dated observations labelled as historical. See router issues [#206](https://github.com/jrwroberts1976/homelab-platform/issues/206) and [#209](https://github.com/jrwroberts1976/homelab-platform/issues/209).
