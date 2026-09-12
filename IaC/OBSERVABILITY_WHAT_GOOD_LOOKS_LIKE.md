# Homelab Observability Platform — What Good Looks Like

## Purpose

This document defines the target state for the homelab observability platform. It exists to keep implementation work aligned to outcomes rather than individual tools.

The goal is not simply to deploy Loki, Alloy, Tempo, Grafana, Prometheus, or an AI integration. The goal is to build a coherent, Dynatrace-style observability capability for the homelab that can answer:

- What is broken?
- What changed?
- Which host or service is affected?
- What evidence explains the failure?
- Is the issue infrastructure, application, network, security, or dependency related?
- What should be checked next?
- How confident are we in that conclusion?

The platform must make those answers faster, more consistent, and more evidence-driven than manually searching individual hosts.

---

## North Star

A good observability platform should allow an operator to start from an alert, degraded service, security event, or user-visible symptom and move through metrics, logs, traces, topology, and recent changes without having to know in advance which system contains the answer.

A typical investigation should look like this:

```text
Alert / symptom
      |
      v
Affected service and host identified
      |
      +--> Metrics show when behaviour changed
      |
      +--> Logs show what the service and host reported
      |
      +--> Traces show where request time or errors occurred
      |
      +--> Topology shows upstream/downstream dependencies
      |
      +--> Change context shows deployments/configuration changes
      |
      v
Evidence-backed diagnosis
      |
      v
Recommended next action
```

The system should feel like one observability platform, not a collection of unrelated dashboards.

---

## What Success Looks Like

The platform is successful when all of the following are true.

### 1. Central visibility

All active infrastructure can be investigated from the central observability platform on `monitor-01` without SSH being the normal first troubleshooting step.

The central platform provides:

- infrastructure metrics;
- service and application metrics;
- host and application logs;
- container logs where relevant;
- synthetic availability checks;
- distributed traces for instrumented applications;
- network/security telemetry;
- alert state;
- topology and dependency context;
- AI-assisted investigation.

SSH remains available for remediation and deep diagnostics, but it is not the primary discovery mechanism.

### 2. Correlated telemetry

Metrics, logs, and traces use a shared identity model so information can be correlated reliably.

Minimum common attributes should include, where applicable:

```text
environment = homelab
host        = <canonical-hostname>
role        = <host-role>
service     = <service-name>
instance    = <service-instance>
```

OpenTelemetry-aware applications should additionally use standard resource attributes such as:

```text
service.name
service.version
deployment.environment
host.name
```

Trace and span identifiers should be preserved in application logs where possible so Grafana can pivot directly between logs and traces.

### 3. Useful, low-cardinality labels

Loki labels must be deliberately controlled.

Good labels include stable dimensions such as:

- environment;
- host;
- role;
- service;
- source;
- job.

High-cardinality values should normally remain inside the log payload rather than becoming labels. Examples include:

- IP addresses;
- request IDs;
- trace IDs;
- container IDs;
- filenames;
- usernames;
- URLs;
- alert signatures;
- arbitrary error messages.

The platform should prefer queryable structured fields over uncontrolled label growth.

### 4. One standard collection layer

Grafana Alloy is the standard telemetry collector for supported Linux hosts.

Alloy should be managed through IaC and used as the common collection layer for:

- systemd journal logs;
- selected local application logs;
- Docker/container logs where applicable;
- Suricata and Zeek logs on `sensor-01`;
- OpenTelemetry ingestion where needed;
- relevant host metadata.

The aim is a repeatable host pattern rather than individually handcrafted logging configurations.

Existing working collectors should only be replaced when the replacement is proven equivalent or better.

### 5. Central storage has a clear purpose

The observability backends have distinct responsibilities:

| Signal | Platform | Purpose |
| --- | --- | --- |
| Metrics | Prometheus | Infrastructure, service and operational time-series data |
| Logs | Loki | Central searchable event and log history |
| Traces | Tempo | Request and dependency tracing |
| Dashboards / Explore | Grafana | Unified operator interface |
| Alerts | Prometheus + Alertmanager | Detection and notification |
| Synthetic checks | Blackbox Exporter | Availability and endpoint validation |

Additional products should only be introduced when they solve a demonstrated problem.

Mimir, Pyroscope, or other components are not required simply to imitate a commercial platform.

---

## Target Architecture

```text
                         HOMELAB OBSERVABILITY

                             monitor-01
        +---------------------------------------------------+
        |                                                   |
        |  Grafana                                          |
        |     |                                             |
        |     +-------- Prometheus ------ metrics           |
        |     +-------- Loki ------------ logs              |
        |     +-------- Tempo ----------- traces            |
        |                                                   |
        |  Alertmanager                                     |
        |  Blackbox Exporter                                |
        |                                                   |
        +----------------------^----------------------------+
                               |
                       telemetry ingestion
                               |
             +-----------------+-----------------+
             |                 |                 |
           Alloy             Alloy             Alloy
             |                 |                 |
          Linux             Docker           Security
          hosts             hosts            sensor
             |                 |                 |
       journald/logs     journal/container  Suricata/Zeek
```

`monitor-01` remains the central monitoring host unless there is a clear capacity, resilience, or architectural reason to change that decision.

---

## Current Starting Point

At the start of this work:

- `monitor-01` already hosts Grafana, Prometheus, Alertmanager and Blackbox Exporter in the IaC-managed monitoring Compose project;
- `monitor-01` receives ASUS router syslog on UDP/5514 via rsyslog;
- no active Loki service exists in the current estate;
- no Promtail service is active;
- primary `PROXMOX` already runs Grafana Alloy and collects its systemd journal;
- that Alloy instance currently points to the retired Loki destination `192.168.2.242:3100` and therefore drops data;
- the existing `PROXMOX` Alloy deployment demonstrates the desired native-host collection pattern and should be repaired rather than discarded;
- `sensor-01` is prepared to emit Zeek JSON for later Loki ingestion;
- `monitor-01` has sufficient initial local disk capacity for a controlled single-node Loki/Tempo deployment, subject to retention controls and ongoing monitoring.

This starting point should be treated as migration evidence, not as an excuse to preserve obsolete destinations or configuration indefinitely.

---

## AI Investigation Layer

AI-assisted investigation is a core requirement of the platform.

The AI layer must not be implemented as a continuous stream of raw logs into a model. Instead, it should retrieve relevant evidence when an investigation is triggered.

### Trigger model

An investigation can begin from:

- an active alert;
- a security detection;
- a manually selected host or service;
- an availability failure;
- an anomaly or threshold breach;
- a user request such as "why was Nextcloud slow at 09:42?".

### Investigation flow

```text
Trigger
  |
  v
Identify affected host/service/time window
  |
  +--> Query Prometheus
  +--> Query Loki
  +--> Query Tempo when relevant
  +--> Retrieve topology/dependency context
  +--> Retrieve recent changes/deployments
  +--> Retrieve active alerts and previous related incidents
  |
  v
AI correlation and reasoning
  |
  v
Structured incident assessment
```

### AI evidence tools

The AI investigator should use narrowly scoped, read-only tools such as:

```text
query_loki(...)
query_prometheus(...)
query_tempo(...)
get_host_inventory(...)
get_service_topology(...)
get_recent_changes(...)
get_active_alerts(...)
get_previous_incidents(...)
```

Arbitrary shell access should not be required for normal AI investigation.

If controlled diagnostics are introduced later, they should be exposed as named, bounded diagnostic actions rather than unrestricted command execution.

### Required AI output

Every AI investigation should distinguish observation from inference and return a consistent structure:

- incident or question being investigated;
- affected host/service;
- investigation time window;
- observed symptoms;
- correlated evidence;
- most likely cause;
- alternative explanations;
- confidence level;
- recommended diagnostics;
- recommended remediation;
- security impact where relevant;
- evidence sources used.

The AI must explicitly say when the available evidence is insufficient.

A confident answer without supporting telemetry is a failure condition.

---

## Security Investigation Outcome

The observability platform should allow network detections to be correlated with host and application context.

For example, a Suricata alert should be enrichable with:

- surrounding Suricata events;
- related Zeek connections and DNS activity;
- source/destination host identity from the network-host inventory;
- host journal entries;
- application/container activity;
- previous observations of the same destination or signature;
- relevant infrastructure changes.

The desired outcome is not simply "an IDS alert occurred" but an evidence-backed assessment such as:

```text
Assessment: likely benign
Confidence: high

Evidence:
- destination maps to a known software repository;
- Docker image pull occurred at the same time;
- no unexpected inbound connection was observed;
- host authentication logs show no associated anomaly.

Action: no immediate response required.
```

The same process must be able to conclude "insufficient evidence" or "investigation required" when appropriate.

---

## Topology and Dependency Awareness

A Dynatrace-style outcome requires the platform to understand relationships, not just individual hosts.

The observability design should eventually model relationships such as:

```text
Nextcloud
  |
  +--> PostgreSQL
  +--> Redis
  +--> local web service
  +--> DNS
  +--> host: cloud-01
```

and:

```text
Internet request
  |
  +--> edge / tunnel
  +--> application
  +--> database/cache
  +--> storage
```

Topology may be derived from a combination of:

- IaC inventory;
- Docker/service discovery;
- OpenTelemetry traces;
- Prometheus target metadata;
- the network-host collector;
- explicit dependency metadata where automatic discovery is unreliable.

The topology model should favour correctness over visual complexity.

---

## Dashboard Outcomes

The platform should provide a small number of operationally useful views rather than a large collection of disconnected dashboards.

Minimum target views are:

### Operations Overview

Shows the current health of the homelab:

- hosts up/down;
- service availability;
- active alerts;
- CPU/memory/storage pressure;
- recent error-rate changes;
- logging/telemetry ingestion health;
- key network/security state.

### Host / Service Investigation

Allows an operator to select a host or service and see:

- health and resource metrics;
- relevant logs;
- alerts;
- recent changes;
- dependencies;
- traces where available.

### Security Operations

Correlates:

- Suricata;
- Zeek;
- router events;
- authentication events;
- network-host inventory;
- suspicious host/service behaviour.

### Web Platform / Analytics

Keeps application and website operational telemetry correlated with existing plans for Cloudflare, Umami, Grafana/Loki and origin health.

### Network Hosts

Uses the network-host data gatherer to provide identity, reachability, ports/services, vendor, latency, status changes and operational/security context.

---

## Alerting Principles

Alerts should identify actionable conditions, not simply interesting data.

Good alerts should answer:

- what is affected;
- how serious it is;
- when it started;
- what evidence triggered it;
- what the operator should investigate first.

Avoid duplicate alerts from multiple systems for the same underlying condition where possible.

AI analysis may enrich an alert, but it must not hide the original alert evidence.

---

## Resilience and Failure Behaviour

The observability platform is itself production infrastructure and must be observable.

We should be able to detect:

- Alloy unable to reach Loki;
- Loki unavailable or rejecting writes;
- Prometheus scrape failures;
- Tempo ingestion failures;
- low disk space or abnormal growth on `monitor-01`;
- telemetry source silence;
- failed containers/services;
- excessive dropped log batches;
- time synchronisation problems that would break correlation.

A telemetry pipeline failure should not remain invisible for days.

---

## Retention and Storage

Retention must be intentional.

The initial system should use controlled local retention appropriate to available `monitor-01` storage. Historical telemetry is useful but is not currently classified as irreplaceable application data.

Retention decisions should balance:

- investigation value;
- storage growth;
- query performance;
- operational complexity.

The platform should measure its own storage growth before retention windows are increased.

Do not introduce complex distributed storage purely to maximise historical retention.

---

## IaC Standard

All durable observability configuration must live under `IaC/`.

This includes:

- Loki deployment and configuration;
- Tempo deployment and configuration;
- Grafana datasource provisioning;
- Alloy installation and configuration;
- common telemetry labels/resource attributes;
- host-specific collection extensions;
- dashboards that are intended to survive rebuilds;
- alert rules;
- validation scripts;
- relevant runbooks.

Manual configuration may be used temporarily for investigation or proof-of-concept work, but it is not considered complete until represented in IaC.

Deployments must be repeatable and should be idempotent where the underlying tooling supports it.

---

## Rollout Sequence

The intended implementation sequence is:

### Phase 1 — Central logging foundation

- Add Loki to the existing `monitor-01` monitoring stack.
- Provision Loki as a Grafana datasource.
- Define initial retention and storage controls.
- Repair primary `PROXMOX` Alloy to send to `monitor-01` rather than retired `192.168.2.242`.
- Prove `PROXMOX -> Alloy -> Loki -> Grafana` end to end.
- Add ingestion-health monitoring.

### Phase 2 — Standard Alloy agent

- Create reusable Alloy IaC role.
- Deploy native Alloy to active Linux hosts in controlled batches.
- Collect journald using the common identity model.
- Add Docker log discovery on Docker hosts.
- Preserve low-cardinality labels.
- Validate no legacy Promtail or obsolete pipelines remain.

### Phase 3 — Security telemetry

After the `sensor-01` capture NIC/SPAN path is validated:

- ingest Suricata `eve.json`;
- ingest Zeek JSON logs;
- correlate with host/network inventory;
- add security investigation views and AI workflows.

### Phase 4 — Tracing / APM

- Add Tempo to the central stack.
- Provision Tempo in Grafana.
- Add OpenTelemetry instrumentation to applications we control where useful.
- Establish metrics/logs/traces correlation.
- Build useful dependency/service views.

### Phase 5 — AI Investigator

- Implement bounded read-only telemetry query tools.
- Trigger investigations from alerts and manual questions.
- Require structured, evidence-backed output.
- Store investigation summaries where useful for later comparison.
- Integrate relevant findings into management/operational reporting.

### Phase 6 — Higher-level observability

Only after the previous layers work reliably:

- topology enrichment;
- deployment/change correlation;
- anomaly detection;
- selected automated diagnostics;
- optional profiling or additional telemetry products if justified.

---

## Definition of Done

A phase is not complete because a container is running or a package is installed.

A phase is complete only when:

1. configuration exists in IaC;
2. deployment is repeatable;
3. the service is healthy after deployment;
4. data is proven end to end;
5. failures of the telemetry pipeline are detectable;
6. Grafana can query/use the resulting data;
7. rollback or rebuild behaviour is understood;
8. secrets are not committed to Git;
9. the implementation has an operational validation check;
10. relevant documentation/runbooks are updated.

For AI features, completion additionally requires:

1. evidence sources are explicit;
2. the model can state insufficient evidence;
3. AI output distinguishes facts from inference;
4. normal operation does not require unrestricted shell access;
5. recommendations can be traced back to telemetry.

---

## Anti-Goals

The project should explicitly avoid the following:

- deploying products solely because Dynatrace has an equivalent feature;
- collecting every available log without an investigation use case;
- sending all raw logs continuously to an AI model;
- uncontrolled Loki label cardinality;
- creating a separate monitoring stack for each workload;
- replacing working telemetry before replacement capability is proven;
- adding distributed storage before scale requires it;
- treating dashboards as the goal rather than investigation capability;
- allowing AI conclusions to replace source evidence;
- giving the AI unrestricted infrastructure control as a shortcut;
- accepting manual configuration as the long-term authority;
- building complex automation that cannot be restored or reproduced from IaC.

---

## Decision Test for Future Work

Before adding a new component, integration, dashboard, collector, or AI workflow, ask:

1. Which operator question does this help answer?
2. Which signal does it improve: metrics, logs, traces, topology, changes, security, or investigation?
3. Can it use the common identity model?
4. Is the data actionable?
5. Is there already a component that provides the same capability?
6. Can it be managed through IaC?
7. How will we know it has failed?
8. Does it improve diagnosis enough to justify its complexity?

If those questions do not have good answers, the work should normally be deferred.

---

## Final Outcome

The finished platform should allow us to ask a question such as:

> Why did this service become slow, fail, or generate a security alert?

and receive an answer built from correlated infrastructure metrics, logs, traces, topology and recent-change evidence, with an AI-generated assessment that clearly states its confidence and supporting evidence.

That is the target. Individual tools are implementation choices in service of that outcome.