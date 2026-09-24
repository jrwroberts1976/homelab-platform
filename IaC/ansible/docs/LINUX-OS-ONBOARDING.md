# Linux OS identification at onboarding

<!-- estate-authority: IaC/inventory/estate.json -->

This is the first stage of OS identification. The controller reads `/etc/os-release` and Ansible facts from an explicitly selected managed Linux host, then writes a private JSON record locally. It does **not** scan the LAN, change a managed host, publish metrics, or claim that an IP-to-MAC mapping has been validated.

The current estate and host identities are governed by `docs/architecture/CURRENT-STATE.md` and `IaC/inventory/estate.json`. The existing Ansible inventory is `IaC/ansible/inventory/hosts.yml`. The repository currently uses service-specific provisioning playbooks rather than a single universal Linux onboarding entry point; this playbook provides a reusable explicit onboarding step without silently changing every existing deployment.

## First approved trial

On `admin-01` in a clean checkout of this branch:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook --syntax-check playbooks/linux-os-onboarding.yml
ansible-playbook playbooks/linux-os-onboarding.yml --limit monitor-01 --check
ansible-playbook playbooks/linux-os-onboarding.yml --limit monitor-01
```

The target must be a Linux host in the authoritative Ansible inventory, reachable through its configured SSH account and verified host key. The playbook requires `--limit` and refuses a hostname mismatch or absent OS identification. It does not require sudo. Avoid running the first trial against every host.

The output is `~/.local/state/homelab-os-facts/monitor-01.json` on the controller, directory mode `0700`, file mode `0600`. This is private operational evidence and should not be committed to Git. The `os_release_text` field retains the actual file contents, including vendor-specific keys; inspect before sharing externally.

## Confidence and identity

A successful direct collection with a matching inventory hostname is classified as verified and assigned 100% in the **rule-based evidence scheme**. It is not a calibrated probability. The stored `inventory_ip` is inventory metadata, **not** proof of current or historical MAC ownership. Join to the network discovery inventory only after validating current MAC/IP ownership and timestamps.

Do not treat Home Assistant OS, network appliances, Windows hosts, or unmanaged devices as ordinary Linux onboarding targets. Nmap and DNS evidence remain separate and never overwrite verified local facts.

## Follow-on integration

After validating the first host, invoke this playbook from the approved Linux provisioning workflow for each newly enrolled managed host. Refresh the record during ordinary configuration management or after an OS upgrade. A later reviewed change will correlate verified host records with Nmap and DNS evidence, export Prometheus metrics and update Grafana. No existing production playbooks or timers are altered by this first-stage PR.
