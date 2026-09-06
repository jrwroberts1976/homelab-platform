# Router Clean-Rebuild Plan

Status: planned maintenance; not yet executed.

Router: ASUS RT-AC86U main router  
Legacy address: `192.168.2.1`  
AiMesh nodes currently known: `192.168.2.181`, `192.168.2.218`

## Goal

Perform a clean firmware/factory-reset rebuild of the router rather than carrying historical configuration forward.

The rebuild will deliberately recreate:

- WAN configuration
- LAN addressing
- DHCP scope
- DHCP reservations
- DNS advertisement
- Wi-Fi / AiMesh
- QoS
- required firewall/port-forward rules
- DDNS/VPN settings where still required
- monitoring/syslog integration

The old configuration is evidence/recovery material only. If the purpose of the reset is to remove historical drift, do **not** blindly restore the old full configuration backup after the reset.

## Pre-reset evidence gate

Before any reset:

- export the current router configuration as rollback evidence
- record firmware version
- record WAN connection type and any ISP-specific requirements
- record LAN subnet/gateway
- export or document DHCP reservations
- record current DHCP lease range
- record DNS server advertisement
- record Wi-Fi SSIDs/security mode without committing passwords
- record AiMesh topology/nodes
- record port forwards
- record VPN server/client configuration
- record DDNS settings
- record MAC filtering/access-control rules
- record QoS state/rules
- record router syslog/monitoring destination
- ensure console/local access and a recovery route are available

Secrets, Wi-Fi keys, ISP credentials and private keys must stay in SOPS or another protected secret store and must never be committed in plaintext.

## Working target LAN services

These remain design inputs until the router audit is complete:

- router/gateway: `192.168.2.1`
- primary DNS: `dns-01` (currently legacy DietPi `192.168.2.48`)
- secondary DNS: `dns-02` after the new VM is deployed
- DHCP remains on the ASUS router unless a later design decision explicitly moves it

## DHCP direction

The clean rebuild should use a documented reservation plan rather than ad-hoc static addressing.

Every infrastructure reservation should record:

- target hostname
- MAC address
- reserved IPv4 address
- device/role
- source-of-truth entry in Git

The final reservation table will be built after target hostnames and switch-port identities are approved.

## QoS direction

QoS will be rebuilt from first principles after the clean reset.

Before defining classes, measure the actual WAN upload/download rates and identify traffic that genuinely needs priority. Avoid preserving old rules without evidence.

Likely priority categories to evaluate:

1. interactive voice/video
2. DNS and essential infrastructure control traffic
3. normal client/web traffic
4. backup/synchronization
5. bulk downloads and non-urgent jobs

The exact ASUS QoS mode and bandwidth values must be decided from the post-reset firmware capabilities and measured WAN performance.

## Cutover safety

A router reset can remove DHCP, DNS advertisement, Wi-Fi and internet access simultaneously.

The reset window must therefore have:

- current config backup available
- local wired admin access
- known router recovery procedure
- Pi-hole/Unbound services confirmed healthy before DNS is advertised
- AiMesh rejoin procedure available
- a written validation checklist

## Validation after rebuild

Prove:

- router reachable at intended management address
- WAN/internet works
- DHCP leases are issued correctly
- reservations resolve to intended devices
- clients receive the intended DNS servers
- both DNS paths resolve successfully
- Wi-Fi and AiMesh operate
- QoS is active with measured bandwidth values
- required port forwards/VPN/DDNS work
- monitoring/syslog is restored
- no legacy configuration was silently reintroduced
