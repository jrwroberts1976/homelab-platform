# Automated network-device identification

<!-- estate-authority: IaC/inventory/estate.json -->

## Current production status

As verified on **29 September 2026**, `monitor-01` is the single active owner of
LAN discovery, selective deep profiling, saved Nmap evidence, DNS evidence
correlation, network inventory publication and generated per-device Grafana
dashboards.

The active identification path is:

```text
current LAN inventory
        |
        v
bounded targeted Nmap profile
(top 100 TCP, service/version light + OS fingerprint)
        |
        +------------------------------+
        |                              |
        v                              v
MAC/vendor + hostname             saved Nmap evidence
                                       |
                                       v
                         dual-Pi-hole DNS evidence lookup
                         dns-01 + dns-02, read-only FTL
                                       |
                                       v
                         bounded DNS signal classification
                                       |
                                       v
                         MAC + Nmap + DNS correlation
                                       |
                                       v
                         network inventory Prometheus metrics
                                       |
                                       v
                         generated Grafana host dashboard
```

This is an evidence pipeline, not an authoritative asset-management engine.
Documented IaC and fresh Zabbix Agent 2 facts remain authoritative where they
exist. Nmap and DNS evidence refine unmanaged/unknown devices and remain
explicitly labelled as inferred/supporting evidence.

## Nmap profiling

The canonical profiler is:

`IaC/ansible/roles/network_host_deep_profiler/templates/homelab-network-host-deep-profiler.py.j2`

Production behaviour:

- owner: `monitor-01`;
- targeted scan only; no broad subnet deep scan;
- top 100 TCP ports;
- `-sV --version-light` service/version evidence;
- Nmap OS fingerprinting with bounded attempts;
- saved state keyed by MAC so DHCP IP changes do not silently create a new
  identity;
- the freshest/current IP for a MAC is selected before profiling;
- completed current devices are re-profiled weekly for changed ports,
  services/version evidence and supporting OS evidence;
- the baseline backlog is spread deterministically across seven days rather
  than scanning the retained estate at once.

For managed Linux hosts, Nmap OS evidence is supporting evidence only. Fresh
Zabbix Agent 2 OS facts take precedence. For unmanaged devices without a
stronger source, a saved Nmap match can be published as `inferred_nmap`.
No match means unknown; the system does not invent an OS.

## Automatic DNS evidence

The canonical role is:

`IaC/ansible/roles/network_host_dns_evidence/`

The timer is enabled on `monitor-01` and normally runs every five minutes.
It does **not** copy raw household DNS history to the monitoring host.

### Resolver-side privacy boundary

Each resolver has a dedicated restricted account and forced command. The
monitor uses a dedicated ED25519 key and pinned resolver host keys. The remote
helper opens Pi-hole FTL read-only and accepts only:

```text
query <LAN-IP> <profiled-at>
```

The helper validates that the IP is in `192.168.2.0/24`.

The query window is bounded to seven days and anchored to the Nmap profile
time. This matters for offline devices: useful DNS evidence can still be
recovered around the time the device was actually observed instead of
searching only the most recent seven days.

The resolver returns only:

- total query count for the bounded window;
- at most five top domains;
- a small reviewed set of classified DNS signals;
- at most three example domains per signal;
- observation/window timestamps.

Full Pi-hole query history stays on `dns-01` and `dns-02`.

### Current signal classes

The resolver-side classifier currently recognises a deliberately small,
reviewable vocabulary including:

- Amazon Fire TV / Amazon Video / Alexa endpoints;
- NordVPN endpoints;
- Windows Update / Microsoft delivery endpoints;
- TP-Link/Tapo cloud endpoints.

A signal is a clue, not proof of device identity. More signal rules should be
added only when their meaning is sufficiently specific and reviewable.

## Correlation and confidence

The monitor-side worker stores protected state in:

`/var/lib/homelab-network-hosts/dns-evidence.json`

It runs once after each completed deep profile, with failed lookups retried
after the configured cooldown. Evidence is versioned so a collector upgrade
can deliberately refresh older records when the interpretation changes.

For Fire TV identification, the current correlation rule is conservative:

1. DNS must contain the Amazon Fire TV signal.
2. MAC vendor and/or Nmap service evidence are used as independent
   corroboration.
3. With at least two supporting evidence sources, the worker publishes:
   `device_hint="Amazon Fire TV / Fire TV Stick"` and
   `confidence="corroborated"`.
4. DNS alone remains only a DNS indication and does not silently become an
   authoritative identity.

The production test case on 29 September 2026 was `192.168.2.8`,
MAC vendor `Amazon Technologies`. The automatic lookup recovered Fire TV /
Amazon Video / Alexa signals from both Pi-holes, a NordVPN signal from
`dns-01`, and correlated that with the existing Nmap
`Amazon FireTV Stick` service evidence. The resulting device hint was
`Amazon Fire TV / Fire TV Stick` with `corroborated` confidence.

## Inventory source precedence

The network inventory exporter is:

`IaC/ansible/roles/monitoring_stack/files/network-device-inventory-exporter.py`

Important precedence rules:

- fresh Zabbix Agent 2 OS facts are authoritative for managed hosts;
- explicit canonical/documented platform identity is retained;
- DNS hints can refine device type and provide supporting clues;
- Nmap OS matches can become the best available inferred OS for unmanaged
  devices;
- automatic DNS evidence is correlated by MAC first, not merely IP, to avoid
  attributing stale DHCP evidence to another device;
- a DNS or Nmap inference never overwrites a stronger authoritative fact.

Published metrics include the current device identity, OS and evidence source,
DNS hint/time, current status, saved Nmap fingerprint and observed services.

## Grafana behaviour

Generated dashboards live in the **Network Hosts** Grafana folder.

The generator is:

`IaC/ansible/roles/monitoring_stack/files/network-host-dashboard-generator.py`

A known hostname is used as the friendly title. For an unknown device whose
hostname is only its IP, a useful inferred device type is preferred while the
IP is retained for disambiguation. For example:

```text
Homelab — Amazon Fire TV / Fire TV Stick (192.168.2.8)
```

The host detail view can show:

- current identity, vendor and device type;
- authoritative/inferred OS and source;
- positively observed open ports and services;
- supporting Nmap OS fingerprint and Nmap-reported accuracy;
- bounded DNS evidence and observation time;
- Linux telemetry panels only when that telemetry actually exists.

An empty Nmap or DNS result is not proof that a device is safe, offline or
fully identified.

## Deployment controls

Stage/update the DNS role without enabling its timer:

```bash
cd /home/james/projects/homelab-platform/IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/network-host-dns-evidence-stage.yml
```

Activate the automatic DNS evidence timer only through the reviewed activation
playbook:

```bash
ansible-playbook -i inventory/hosts.yml \
  playbooks/network-host-dns-evidence-activate.yml
```

Verify:

```bash
systemctl is-enabled homelab-network-dns-evidence.timer
systemctl is-active homelab-network-dns-evidence.timer
systemctl list-timers homelab-network-dns-evidence.timer --no-pager
```

The current production verification returned `enabled`, `active` and a
next run approximately five minutes later.

## Important limits and remaining stages

The following are **not** automatically authoritative today:

- DNS evidence;
- Nmap OS guesses;
- future AI assessments.

The current live automation stops at evidence-qualified device identification,
inventory publication and Grafana. The broader workflow described in
[Selective device identification](unknown-device-reconciliation.md) still
contains later planned stages such as AI assessment, manual-input escalation
and persistent generated GitHub host pages. Those future stages must not be
described as deployed until separately implemented and verified.
