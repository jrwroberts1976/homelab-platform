# Network baseline — 24 September 2026

## Sources

- Canonical identity and addressing: `IaC/inventory/estate.json` (validated 17 September 2026).
- Architecture and service roles: `docs/architecture/CURRENT-STATE.md`.
- Nmap observations collected from `monitor-01` (`192.168.2.52`).
- ASUS router DHCP/ARP collector database on `monitor-01`.

`consolidated-inventory.csv` is an observational snapshot, not deployment authority.

## Reconciliation

| Evidence category | Address records |
|---|---:|
| Nmap scan and ASUS router | 39 |
| Nmap only (router itself, `.1`) | 1 |
| Canonical scanner self (`.52`) | 1 |
| ASUS router only, unconfirmed | 6 |
| **Total** | **47** |

All 20 canonical assets are represented. No duplicate IP records or
duplicate observed Nmap MACs were found. No MAC mismatches were reported
where both Nmap and the router supplied a MAC.

## Outstanding investigations

- `.6` (`LAPTOP-SRR7CFCE`), `.155` (`XS0B-iR_5B10EC`) and `.224`
  (`POCO-C75`) were router-reported online with recent DHCP observations,
  but none answered the direct ARP check at 13:18 BST.
- `.8`, `.123` and `.144` were router-only, unconfirmed records.
  The router associated `.144` with its own MAC; this requires investigation.
- `.196` was formerly used by `media-01` when it was a Kubernetes host.
  It is excluded as a separate active asset, but an ARP packet trace showed
  that `.195`'s MAC also answers for `.196`. The cause is unresolved.
- `monitor-01` was omitted from its own ARP discovery and included from
  canonical identity and its confirmed role as the scanner.

## Scan coverage and limitations

- ARP discovery covered `192.168.2.0/24`.
- The successful quick TCP scan covered Nmap's top 100 TCP ports.
- Service detection covered 16 selected TCP ports.
- The initial combined TCP/OS scan timed out and provides no reliable
  OS fingerprint evidence.
- No comprehensive TCP-port scan or UDP service scan was completed.
- Router online status is not independent proof of current reachability.
- Nmap service names marked uncertain are hints, not verified identities.

The raw Nmap XML and router database remain on `monitor-01` under the
original collection environment. This repository snapshot contains the
consolidated CSV and its interpretation.
