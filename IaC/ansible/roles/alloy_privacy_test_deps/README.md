# Alloy Pi-hole privacy-test dependencies

Opt-in Ansible role for synthetic Loki-payload tests on DNS resolvers. Installs Debian's Python 3.13 venv support and a root-owned isolated Python environment with `python-snappy` and `protobuf`. No global pip packages, no production Alloy config changes, no Loki credentials, no firewall changes.

From `IaC/ansible`:

```bash
ansible-playbook playbooks/alloy-privacy-test-deps.yml --syntax-check
ansible-playbook playbooks/alloy-privacy-test-deps.yml --limit dns-01 --check --diff
ansible-playbook playbooks/alloy-privacy-test-deps.yml --limit dns-01
ansible dns-01 -b -m command -a '/opt/homelab/alloy-privacy-test/venv/bin/python -c "import snappy, google.protobuf; print(\"OK\")"'
```

The role provisions only decoding dependencies; it does **not** run the synthetic privacy test or authorise live Pi-hole log shipping. Production deployment requires an isolated end-to-end test that proves the receiver gets only allowlisted event tokens and no raw domains/client identifiers. Run on dns-02 only if needed. To remove test tooling later, use a separate approved cleanup change.
