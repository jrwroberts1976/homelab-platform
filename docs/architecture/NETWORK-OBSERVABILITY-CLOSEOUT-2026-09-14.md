# Network Observability Close-Out — 14 September 2026

This note records the live validation used to close the current Network Hosts enrichment and HP ProCurve telemetry development work.

## Network Hosts platform

Validated on `Proxmox-2` (`192.168.2.71`).

### Discovery collector

- `homelab-network-host-collector.timer` enabled and active.
- approximately five-minute discovery cadence.
- live inventory updating under `/var/lib/homelab-network-hosts/inventory.json`.

### Enrichment

A manual validation run completed successfully before periodic execution was enabled.

Observed result:

```json
{
  "event": "network_host_enrichment_complete",
  "online_hosts_scanned": 34,
  "proxmox_guests_matched": 3,
  "scan_errors": {},
  "service_endpoints": 57,
  "tls_certificates": 11
}
```

Validation also proved:

- `/var/lib/homelab-network-hosts/enrichment.json` refreshed successfully;
- JSON parsed successfully with `jq`;
- Prometheus textfile metrics were regenerated;
- `Result=success`;
- `ExecMainStatus=0`;
- `homelab-network-host-enricher.timer` enabled and active.

The production playbook now encodes the timer as desired state while the reusable role keeps its disabled-by-default safety behaviour.

### Deep profiling

- `homelab-network-host-deep-profiler.timer` enabled and active.
- deep-profile state and Prometheus metrics continued to update during validation.

The active Network Hosts pipeline is therefore:

```text
periodic discovery
    -> persistent inventory
    -> periodic enrichment
    -> service / TLS / Proxmox context
    -> one-time deep profiling for newly discovered hosts
    -> Prometheus / Grafana
```

## HP ProCurve telemetry

Validated on `monitor-01` (`192.168.2.52`) against the HP ProCurve 2510G-24 at `192.168.2.16`.

Initial deployment correctly failed closed because an incorrect SNMP community was supplied. Diagnostic testing proved:

- IP connectivity to the switch was healthy;
- UDP/161 requests left `monitor-01`;
- the switch did not answer the incorrect community;
- explicit SNMP v1 and v2c requests using the validated community succeeded;
- request and response packets were observed on the wire.

After the protected SNMP configuration was reconciled, the IaC deployment completed with:

```text
monitor-01 : ok=18 changed=1 unreachable=0 failed=0
```

Live validation then proved:

- protected SNMP configuration matched the validated community;
- `homelab-hp-switch-collector.service` returned `Result=success` and `ExecMainStatus=0`;
- `homelab_switch_up{switch="hp-switch"} 1`;
- switch uptime exported successfully;
- `/var/lib/homelab-switch-collector/topology.json` exists and is valid JSON;
- topology file size was approximately 11 KiB at validation time;
- `homelab-hp-switch-collector.timer` enabled and active;
- Node Exporter exposes the switch metrics;
- zero failed systemd units remained on `monitor-01`.

The collector writes topology and forwarding-table state locally and exports switch/port metrics through the Node Exporter textfile collector for Prometheus/Grafana.

## Security note

The current ProCurve still uses SNMP v1/v2c community authentication. The validation packet capture demonstrated that the community value is visible in plaintext on the LAN.

The current credential must therefore be treated as a credential despite the protocol's weak protection. Replacing or restricting the unrestricted community remains a network-hardening task.

No SNMP credential value is recorded in this document or Git.

## Development status

The following work is closed as implemented:

- Network Host discovery;
- periodic host enrichment;
- one-time deep profiling;
- Network Hosts Prometheus metrics;
- first-seen device notification;
- Network Hosts Grafana dashboards;
- HP ProCurve SNMP telemetry into Prometheus/Grafana.

The next primary development work should move to backup/recovery, controlled lifecycle management and higher-value analytics rather than rebuilding these completed foundations.
