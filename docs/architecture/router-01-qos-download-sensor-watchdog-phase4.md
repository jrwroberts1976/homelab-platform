# Phase 4: sensor-01 isolated independent-watchdog design

Status: **design and read-only preflight only**. No runtime activation.

## Separation and non-negotiable boundaries

- admin-01 remains an SSH/Ansible/Git jump box; do not host persistent QoS testing services there.
- sensor-01 retains existing Zeek/Suricata/capture responsibilities for now. Failed IDS units are a separate issue, not a reason to alter them in this test.
- router-01 physical eth1 has working 13 Mbit CAKE upload shaping. No router WAN, PPPoE, DNS, DHCP, firewall, or live download IFB changes are allowed by this phase.
- A disposable, unconnected network namespace on sensor-01 will hold dummy ingress and IFB interfaces. Never attach ingress filters to eth0, ppp0, or other existing production interfaces.
- All changes are via versioned Ansible and approval gates. The preflight in this branch is read-only.

## Watchdog design gates prior to implementing activation

1. Use a collision-checked per-run identifier for a namespace, marker directory, and *separate* transient watchdog unit; refuse pre-existing resources rather than adopt or delete them.
2. Retain a namespace owner/keeper that survives the installer and its supervising launcher, so the watchdog can still enter the same namespace. Validate inode identity from /proc/.../ns/net before every write; never accept host namespace identity.
3. Arm the watchdog **before** installing IFB or the ingress redirect; verify its start and deadline independently, and refuse to proceed on failure. The watchdog must not be a child process of the installer.
4. The watchdog cleanup must independently identify the exact owned dummy, IFB, tc handle/pref and namespace. Refuse ambiguous ownership or foreign filters and report incomplete cleanup as a failure.
5. Inject a real SIGKILL into installer and supervisor while the independent unit is still alive, then verify watchdog execution, absence of owned filters/IFB, and no surviving test units/resources.
6. Exercise an installer/watchdog race, repeated up/down notifications, foreign ingress filters, interface identity replacement, and timeout. Use strict locking and bounded waits; never use broad `pkill`, `tc qdisc del dev eth0`, or generic cleanup.
7. Capture systemd unit properties/journal and test markers before cleaning the run state; publish bounded evidence to GitHub only after review.
8. Make final teardown resilient to Ansible interruption and explicitly document emergency cleanup. Confirm sensor-01 default route, SSH, and IDS service state unchanged.

## Present evidence

- Earlier isolated real CAKE/IFB test on admin-01 passed (5 OK, 1 changed).
- Earlier isolated child SIGKILL cleanup test on admin-01 passed (5 OK, 1 changed); its surviving parent cleaned up. **This did not prove an independently scheduled watchdog.**
- sensor-01 inspection showed 2.5 GiB available RAM, 64 GiB available disk, required networking tools and kernel modules, and successful creation of a loopback-only network namespace. systemd was degraded because two sensor units failed; do not change their state during QoS testing.
- Next: run `router-01-qos-download-sensor-watchdog-preflight.yml` with syntax-check and then read-only execution. Do not implement the runtime test before inspecting its result and agreeing on ownership/cleanup strategy.
