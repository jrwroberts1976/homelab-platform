# Security and Monitoring Integration Closure — 7 October 2026

**Status:** COMPLETE  
**Scope:** Prioritised Project 2 in `ACTIVE-INFRASTRUCTURE-BACKLOG.md`  
**Authority:** live validation plus current IaC/current-state documentation

## Closure decision

Project 2 is closed as complete. The platform has demonstrated end-to-end monitoring and passive-security coverage without requiring additional speculative tooling.

CrowdSec is not installed in the active estate and is not a dependency of the current monitoring, sensor or management-report pipeline. Its absence is deliberate and must not be represented as a telemetry gap.

## Live validation summary

### Core monitoring platform — `monitor-01`

Validated 7 October 2026:

- no failed systemd units;
- Prometheus running and ready;
- Alertmanager running and ready;
- Loki running and ready;
- Grafana running with database health `ok`;
- Blackbox Exporter running;
- all active Prometheus targets reported `up`;
- no non-healthy Prometheus targets were returned.

The healthy target set included DNS probes, ICMP probes, PVE HTTPS probes, Loki, Prometheus and node exporters for the current monitored estate.

### Passive security sensor — `sensor-01`

Validated 7 October 2026:

- Suricata enabled and active;
- Grafana Alloy enabled and active;
- Prometheus node exporter enabled and active;
- managed `homelab-zeek.service` enabled and active;
- `zeekctl status` reports the standalone Zeek worker running;
- `homelab-zeek-flow-summary.timer` enabled and active;
- live Zeek connection, DNS, HTTP, SSH, SSL, notice and supporting logs present;
- Zeek `conn.log` populated and current;
- Zeek Community ID present on live connection telemetry;
- 24-hour Zeek flow summary generated successfully.

Capture-quality evidence showed:

```text
Zeek packet loss:                  0.0%
Zeek gaps:                         0
Suricata kernel drop percentage:   approximately 0.0002%
Configured Suricata warning level: 0.1%
Configured Zeek warning level:     0.5%
Capture health:                    healthy
```

The dedicated capture interface was reported present, up, carrier-on and promiscuous.

### Sensor evidence integration

The management-report evidence pipeline received schema-v2 evidence from `sensor-01` with:

- `status: ok`;
- `assurance_gap_count: 0`;
- no assurance gaps;
- Suricata 24-hour coverage `complete` with warm-up complete;
- Zeek 24-hour coverage `complete`;
- capture health `healthy`;
- Suricata and Zeek both reported active.

The evidence contained bounded 24-hour Suricata alert summaries and Zeek connection/DNS/SSL/notice summaries. Individual detections and notices remain operational security signals to investigate or tune as appropriate; they are not evidence that the integration platform is incomplete.

### Zabbix platform — `zabbix-01`

Validated 7 October 2026:

- no failed systemd units;
- `zabbix-server` active;
- `zabbix-agent2` active;
- PostgreSQL active;
- nginx active;
- PHP-FPM active;
- no recent matching Zabbix server errors were returned by the closure check.

## CrowdSec boundary

A targeted repository search across the active management-report, monitoring-stack, network-sensor and Zeek roles/playbooks returned no `crowdsec` or `cscli` references.

Therefore:

- CrowdSec is not a current telemetry source;
- CrowdSec is not required to close Project 2;
- future CrowdSec adoption would be a separately approved capability change rather than completion work for this project.

## Operational signals observed during closure

The live sensor was detecting real traffic and producing notices/alerts. Examples observed during closure included SSL certificate-validation notices and Suricata informational/signature matches.

These are intentionally treated as normal security-operations inputs. A particular alert may justify investigation or tuning, but the existence of detections is not an integration defect and does not keep the platform project open.

## Completion criteria satisfied

Project 2 is complete because the current estate demonstrates:

1. healthy monitoring services;
2. healthy monitored-target reachability;
3. active passive capture;
4. active Suricata and Zeek processing;
5. bounded, current security evidence;
6. complete 24-hour Suricata and Zeek coverage;
7. no evidence-assurance gaps;
8. healthy capture quality below configured warning thresholds;
9. integration into the management-report evidence path;
10. a clear boundary that excludes absent CrowdSec telemetry.

No additional security product is required merely to claim project completion.

## Ongoing operations

After closure, the following are normal operations rather than backlog blockers:

- investigate genuinely actionable Suricata/Zeek detections;
- tune noisy signatures/notices only when evidence demonstrates value;
- monitor capture loss/drop thresholds;
- maintain Prometheus/Zabbix/Loki/Grafana service health;
- keep sensor evidence freshness and coverage checks working;
- add new security tooling only through a deliberate, separately scoped change.
