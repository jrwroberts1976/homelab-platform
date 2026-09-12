# Homelab Mail Relay Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Host:** `mail-relay-01.jameshouse`  
**IPv4:** `192.168.2.54`  
**Placement:** CT 102 on `PROXMOX` / `192.168.2.70`  
**Status:** operational  
**Last current-state review:** 12 September 2026

## Purpose

`mail-relay-01` provides a single internal SMTP submission point for homelab services and relays approved mail through Gmail's authenticated smart host.

The design keeps upstream Gmail credentials on one dedicated relay rather than distributing them to every application.

## Current live state

Validated 12 September 2026:

- Debian 13 LXC, CT 102 on `PROXMOX`;
- Postfix active/enabled;
- SMTP listening on `192.168.2.54:25` over IPv4;
- `postfix check` clean;
- mail queue empty at validation time;
- local DNS for `.54` resolves correctly;
- SMTP connect/banner/QUIT from `admin-01` succeeds;
- Node Exporter active/enabled on TCP/9100;
- Prometheus ICMP target `up`;
- Prometheus Node Exporter target `up`;
- zero failed systemd units.

No test email was sent as part of the original read-only audit. The later monitoring deployment did not alter Postfix relay configuration or send mail.

## Upstream relay

Current effective Postfix configuration includes:

```text
relayhost = [smtp.gmail.com]:587
smtp_tls_security_level = encrypt
smtp_sasl_auth_enable = yes
smtp_sasl_security_options = noanonymous
```

SASL credential mapping uses:

```text
hash:/etc/postfix/sasl_passwd
```

Credential contents must never be committed to Git or printed into documentation, chat, CI logs or validation transcripts.

## Identity

Current effective identity values include:

```text
myhostname = mail-relay-01.jameshouse
mydomain = jameshouse
myorigin = $myhostname
inet_interfaces = all
inet_protocols = ipv4
```

The relay is intended for internal homelab use and is not a public Internet SMTP server.

## Internal relay ACL

The current `mynetworks` policy is intentionally restricted.

Observed allowed infrastructure addresses include:

```text
127.0.0.0/8
192.168.2.50
192.168.2.51
192.168.2.52
192.168.2.53
192.168.2.70
192.168.2.71
```

Do not broaden this list merely for convenience. Add a new sender only through a reviewed change that identifies the service need and validates relay behaviour.

`admin-01 .48` was able to connect to the SMTP listener during the audit, but connection reachability alone is not proof that the host is permitted to relay mail under Postfix policy.

## Application use

Applications that need email should normally submit to:

```text
mail-relay-01.jameshouse
192.168.2.54:25
```

Current IaC documentation includes `cloud-01` / Nextcloud as a relay client.

Individual applications should not need direct Gmail smart-host credentials when the relay meets their requirements.

## IaC ownership

Current relevant paths include:

```text
IaC/ansible/playbooks/mail-relay.yml
IaC/ansible/playbooks/node-exporters.yml
IaC/ansible/roles/
IaC/ansible/roles/monitoring_stack/
IaC/terraform/proxmox/mail-relay/
```

Protected controller-side configuration is expected outside Git, including:

```text
~/.config/homelab-iac/mail-relay.env
```

Exact secret values must not be displayed or committed.

## Controller

Normal reconciliation is launched from:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

The retired TestServer identity must not be used as the normal controller.

## Validation

Non-secret local checks on the relay include:

```bash
postfix check
systemctl is-active postfix
systemctl is-active prometheus-node-exporter
systemctl --failed --no-pager
postqueue -p
ss -ltnp | grep ':25'
ss -ltnp | grep ':9100'
```

A basic network-level SMTP check from an approved client can prove listener/banner behaviour without sending mail.

Actual relay-delivery testing should be deliberate because it sends an external message and exercises protected upstream credentials.

## Monitoring

Host-level monitoring is operational.

Validated 12 September 2026:

- Node Exporter installed through the shared `node_exporter` role;
- second focused Ansible apply reported `changed=0`, `failed=0`;
- TCP/9100 reachable from `admin-01`;
- remote metrics retrieval returned `node_uname_info`;
- Prometheus ICMP target for `.54` is `up`;
- Prometheus Node Exporter target for `.54:9100` is `up`;
- overall Prometheus target state after deployment was 25 active / 25 healthy / 0 unhealthy;
- active Prometheus alerts remained 0;
- Postfix remained active and the queue remained empty.

Future service-specific monitoring may consider:

- Postfix service state;
- queue depth/age;
- smart-host delivery failures;
- TLS/SASL failures;
- disk/log capacity;
- a low-noise end-to-end mail test only if it can be made operationally useful.

## Recovery model

The relay should be reproducible from IaC plus protected secret material.

Recovery order:

1. restore/rebuild the CT at the approved identity;
2. restore protected SMTP credential material outside Git;
3. apply the Postfix Ansible configuration;
4. run `postfix check`;
5. prove listener reachability from an approved internal client;
6. inspect the queue;
7. perform one deliberate end-to-end delivery test if required;
8. revalidate application mail clients;
9. restore Node Exporter/Prometheus host monitoring.

Do not publish Gmail credentials into application configuration merely to bypass a relay incident.

## Definition of current operational state

The service is operational because:

- CT 102 is running at `.54`;
- Postfix is active/enabled;
- SMTP listener is available on TCP/25;
- upstream smart-host/TLS/SASL configuration is present;
- Postfix configuration validation succeeds;
- queue was empty during validation;
- Node Exporter is active and scraped successfully;
- ICMP and Node Exporter Prometheus targets are `up`;
- zero failed units were observed.

Outstanding work:

- service-specific mail metrics/alerting where useful;
- dedicated recovery runbook testing;
- backup/recovery integration where useful.
