# Host AI Intelligence and CVE Correlation Work Plan

**Status:** ACTIVE DEVELOPMENT  
**Opened:** 2026-09-30  
**Authority:** This document tracks the current host-intelligence development phase. It does not supersede `docs/architecture/CURRENT-STATE.md` or `IaC/inventory/estate.json`. AI output is advisory and must never replace deterministic infrastructure facts.

## Goal

Build a bounded, evidence-led host-intelligence layer for the homelab that explains what each host is, what it is doing, what security and patching evidence exists, and what requires operator attention.

The system must distinguish:

- confirmed facts from direct evidence;
- cautious inferences from AI interpretation;
- unavailable or stale evidence from healthy state;
- vulnerability findings from patch availability;
- suspicious DNS behaviour from ordinary browsing/activity.

## Completed foundation

The host-discovery and naming phase is considered complete for now.

Implemented foundations include:

- active network discovery and current online/offline status;
- stable MAC-keyed device identity;
- canonical/friendly host naming;
- ASUS/router hostname evidence;
- DNS identity evidence from `dns-01` and `dns-02`;
- targeted deep profiling;
- saved Nmap OS fingerprints;
- observed TCP/UDP service and port evidence;
- per-host Grafana dashboards;
- automatic dashboard generation for discovered hosts;
- conditional panels based on available telemetry;
- first-seen notifications;
- preservation of stronger OS evidence when a later retry is weaker;
- removal of unidentified IP-only hosts from the published host directory.

## AI host-intelligence evidence sources

The AI assessment is being built from bounded evidence only.

### 1. Canonical estate and inventory

Inputs may include:

- canonical hostname;
- current IP;
- stable MAC;
- documented role and device kind;
- documented OS;
- architecture and kernel where known;
- current online/offline state and last-seen evidence.

Authoritative inventory facts always take precedence over AI inference.

### 2. ASUS/router evidence

Bounded inputs may include:

- router-observed hostname;
- DHCP hostname;
- current or historical IP association;
- router last-seen/presence context.

Router presence is not authoritative when active network discovery provides a newer presence result.

### 3. Nmap and deep profiling

Inputs may include:

- saved OS matches;
- Nmap-reported match score;
- scanned IP;
- TCP/UDP ports;
- service/product/version observations;
- scan time and profile status.

Nmap accuracy values are match scores, not probabilities.

### 4. DNS identity evidence

Existing resolver-local analysis may provide:

- top bounded domains;
- locally classified ecosystem signals;
- device hints;
- confidence and supporting evidence.

Full DNS history remains on the Pi-hole resolvers.

### 5. Recent DNS security activity — last 1 hour

Target behaviour:

- inspect only the previous hour for the current host IP;
- prefer suspicious or blocked DNS attempts over ordinary browsing history;
- classify locally where possible;
- categories of interest include malware/phishing, adult content, gambling, VPN/proxy/Tor and other high-risk or policy-blocked destinations;
- send only bounded category/domain evidence to the AI layer;
- do not export bulk DNS history.

DNS evidence indicates network requests, not user intent.

### 6. Loki — last 24 hours

Host-scoped Loki evidence is bounded before AI use.

Current design includes:

- 24-hour host window;
- bounded sampled entry counts by job/source;
- up to 20 distinct warning/error-style samples;
- filtering for error, failed, critical, warning, timeout, unreachable, OOM, segfault and similar operational signals;
- redaction of messages likely to contain passwords, tokens, API keys, cookies, sessions or bearer credentials;
- removal of IP and MAC addresses from sampled messages.

A lack of warning/error samples is not proof that a host is healthy.

### 7. Zeek

Where host-specific evidence exists, bounded inputs may include:

- connection counts;
- top services;
- top ports.

### 8. Greenbone vulnerability evidence

Current host-scoped inputs include:

- scan/report timestamp;
- report ID;
- task name;
- finding host/IP;
- affected port;
- NVT OID;
- finding name;
- Greenbone score;
- severity;
- actionable finding count.

Only findings matching the current host IP are attached to that host.

An empty match means no matching actionable finding exists in the supplied evidence. It does not prove the host is vulnerability-free or fully scanned.

### 9. Patching status

Host intelligence should include deterministic patch evidence where available:

- updates available;
- security updates available;
- reboot required;
- unattended-upgrades enabled;
- last successful patch evidence/time;
- freshness of patch evidence.

Patch state remains factual evidence. AI may explain the significance but must not invent a patch result.

## CVE phase — current work

**Development status (2026-09-30):** CVE extraction is implemented in the Greenbone scan parser and passed through to the bounded host-AI Greenbone evidence structure. Regression tests cover single, multiple, absent, non-CVE and bounded-reference cases. Production validation completed successfully on greenbone-01: the CVE-aware runner compiled and deployed, the fresh managed scan exited 0/SUCCESS, and evidence was regenerated under report bbfa16af-21a8-4443-ac78-0b9a3f3fe496 at 2026-09-30T09:20:36Z. That scan contained no actionable findings, so there were no live CVE-bearing findings to exercise in production.

Historically, the Greenbone managed evidence exported NVT OID, finding name, score, severity, host and port but did not export CVE references. The development change now extracts bounded CVE references from each NVT result.

### Required CVE changes

1. Parse CVE references from each Greenbone NVT result.
2. Store CVEs as a bounded list in the managed evidence JSON.
3. Preserve the existing finding schema fields.
4. Pass CVE references through the Greenbone publication and management-report evidence path.
5. Include CVEs in host-scoped AI evidence.
6. Add regression tests for:
   - one finding with one CVE;
   - one finding with multiple CVEs;
   - findings without CVEs;
   - malformed/non-CVE references being ignored;
   - bounded output.
7. Expose current CVE exposure in the per-host Grafana security/AI view.
8. Correlate vulnerability exposure with deterministic patch status where evidence supports it.

### Patch-to-CVE correlation rule

The system may state that a host has both:

- an observed Greenbone finding referencing a CVE; and
- outstanding security updates.

It must not claim that a specific pending package update fixes a specific CVE unless package/CVE evidence explicitly establishes that relationship.

## AI assessment output

Each current assessment should provide:

- concise host summary;
- confirmed facts;
- cautious inferences;
- inferred device type;
- inferred platform family;
- identity confidence;
- OS confidence;
- manual-review flag;
- assessment timestamp;
- model identifier.

The assessment state keeps a bounded history so changed conclusions can be reviewed.

## Scheduling

Target behaviour:

- new devices: first AI assessment approximately one hour after first identification, allowing discovery/DNS/profile evidence to settle;
- evidence change: reassess on the next resolver run;
- unchanged existing hosts: refresh weekly;
- unassessed hosts take priority over routine refreshes.

## Safety and data-minimisation rules

- AI never overrides canonical hostname, authoritative OS, patch facts, Greenbone findings, presence or directly observed ports/services.
- Keep secrets and credentials outside Git and out of AI payloads.
- Do not send full raw Loki logs.
- Do not send bulk Pi-hole query history.
- DNS requests are behavioural evidence, not proof of user intent.
- Missing telemetry must be represented as unavailable/not assessed, never healthy.
- Greenbone absence of findings is not equivalent to a clean vulnerability assessment unless scan coverage is explicitly proven.
- AI output is advisory and must remain visibly separated from deterministic evidence in Grafana.

## Current implementation state

Implemented in development:

- bounded AI resolver scaffold on `monitor-01`;
- Greenbone CVE extraction with up to 20 unique CVE references per finding;
- production Greenbone CVE-aware scan runner validated successfully on greenbone-01;
- conditional per-host Greenbone CVE exposure metrics/panel deployed to monitor-01; 49 MAC-linked host dashboards regenerated successfully and Grafana API validation passed;
- regression coverage for Greenbone CVE extraction;
- deterministic per-host patch evidence from Prometheus (updates, security updates, reboot-required, unattended-upgrades and patch freshness), live-validated across all 15 managed hosts on 2026-09-30;
- Greenbone host-scoped evidence source;
- 24-hour bounded Loki evidence source;
- one-hour bounded DNS request path under development;
- weekly refresh logic;
- one-hour initial-assessment delay for new devices;
- bounded five-assessment history;
- AI fields exposed through the MAC-keyed device-card metric;
- conditional Grafana `AI host intelligence — advisory` panel.

The AI timer remains disabled by default while development and validation continue.

## Work sequence from here

1. **CVE extraction from Greenbone — COMPLETE**
2. **Production CVE evidence regeneration — COMPLETE**
3. **Add host-level CVE exposure to correlated metrics/Grafana — DEPLOYED 2026-09-30**
4. **Add deterministic patch status to the AI evidence packet — LIVE VALIDATED 2026-09-30**
5. Complete the one-hour suspicious/blocked DNS classification path.
6. Validate bounded 24-hour Loki evidence.
7. Run isolated AI assessments against representative hosts.
8. Review hallucination/overreach behaviour and confidence handling.
9. Deploy resolver to `monitor-01` with timer disabled.
10. Run manual production evidence tests.
11. Enable the hourly resolver timer only after review.
12. Observe new-host one-hour analysis and weekly refresh behaviour.
13. Reconcile `ACTIVE-INFRASTRUCTURE-BACKLOG.md` and formally close this Project 3 phase when proven.

## Completion criteria

This phase is complete when:

- CVE references are captured and correlated to host findings;
- patch and vulnerability state are visible per host;
- suspicious/blocked recent DNS activity is represented safely;
- Loki, Zeek, Nmap, DNS, Greenbone and canonical inventory evidence are bounded and provenance-preserving;
- AI summaries clearly separate facts and inferences;
- representative hosts have been reviewed manually for accuracy;
- missing evidence never appears as healthy evidence;
- Grafana shows useful AI intelligence only when an assessment exists;
- scheduled refresh behaviour is proven;
- repository documentation and backlog reflect the resulting live state.
