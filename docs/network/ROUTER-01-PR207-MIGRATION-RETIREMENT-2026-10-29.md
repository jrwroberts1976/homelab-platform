<!-- estate-authority: IaC/inventory/estate.json -->
# Obsolete Pi router migration draft PR #207 — supersession record (29 October 2026)

**STATUS: historical IaC plan only; do NOT execute or merge the original draft.**

The [2026-10-27 draft PR #207](https://github.com/jrwroberts1976/homelab-platform/pull/207) was written when converting the `docker-01` / BirdNET proof-of-concept or a staged Pi to become an Internet router. It includes temporary Kea DHCP service on `192.168.3.1`, delayed Ethernet/IP/PPPoE cabling changes and systemd rollback timers, router firewall and LAN switch scripts, Netplan/NetworkManager migration, and an approval-gated **Docker retirement** writer that would stop BirdNET and Komodo services and remove `docker.io`/Compose/containerd/runc on **`docker-01 192.168.2.220`**.

**These are no longer valid change instructions.** The operator already verified a distinct physical Raspberry Pi `router-01` at `192.168.2.1` is the working PPPoE gateway with nftables/NAT, Unbound DNS and **dnsmasq**, not Kea; the single live DHCP pool is `192.168.2.100–199`. On 29 October an approval-gated Ansible playbook installed and independently verified a MAC-bound ASUS Bedroom `192.168.2.180` DHCP reservation; the pool remains unchanged. Both ASUS units remain reachable (Home `192.168.2.2` static AP, Bedroom `.180` DHCP reserved), and `media-01` `192.168.2.195` is confirmed DHCP-managed. Pi DNS and outside HTTPS were verified from `admin-01`.

Current `docker-01 192.168.2.220` is a **separate in-use Docker/BirdNET/Komodo host**, not the new physical `router-01`. **Never run the PR #207 Docker retirement playbooks on that live host merely to tidy the migration branch.** They were designed to remove live packages/containers, and could interrupt existing BirdNET and Komodo workloads. This closure record is **not** authorisation to stop or decommission anything. The original PR branch and source remain available for historical examination; they should not form the base of a new live router configuration.

## Disposition of original draft content

| Historical #207 work | Disposition |
|---|---|
| Pi PPPoE, `.3.1`, Kea, Netplan, router LAN/NAT switches and rollback timers | Obsolete. Current `.2.1` Pi cutover has its own verified production implementation; **no transplant of old writer code** |
| `docker-01` Docker/BirdNET/Komodo retirement and package removal | **Not authorised**. Preserving active Docker workloads is the current requirement; any retirement is a wholly separate future infrastructure project |
| Historical router migration observations and diagnostic evidence | Preserved by Git history and old PR; not treated as current estate truth |
| DHCP reservations/static overlap | Tracked by issue #206. Bedroom `.180` completed; `media-01 .195` is DHCP, and optional separate `.195` reservation requires MAC verification; never deploy obsolete `.181/.195` split pool |
| Router diagnostics, secure telemetry/SSH tunnelling | Tracked under issue #209, with independent `.2.1`-scoped read-only monitoring audit merged by PR #221; SSH/package writers remain unapplied |

## Boundaries and next steps

No command in this document performs changes. The live `docs/architecture/CURRENT-STATE.md` and `gpt-handover.md` take precedence over dated migration plans; canonical `IaC/inventory/estate.json` still needs a separate, independently validated current-state reconciliation. Any remaining security, Docker lifecycle, or router tooling changes must start from **current main**, use Ansible/IaC with a narrow PR, exact host/IP/service gates, backups and rollback, and obtain distinct user approval for any live restarts or package removals.

The obsolete draft [PR #207](https://github.com/jrwroberts1976/homelab-platform/pull/207) was **CLOSED AS SUPERSEDED, NOT MERGED** on 29 October after reviewed docs-only PR #222 merged and its estate/documentation guard passed. The independent stale diagnostics draft [PR #210](https://github.com/jrwroberts1976/homelab-platform/pull/210) was also closed as superseded after read-only audit PR #221 merged; remaining diagnostics and telemetry backlog is in issue #209. Closing either PR did not delete its branch or commits.
