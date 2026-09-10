#!/usr/bin/env bash

set -u

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

MAIL_RELAY_HOSTNAME="${MAIL_RELAY_HOSTNAME:-mail-relay-01}"
MAIL_RELAY_IPV4="${MAIL_RELAY_IPV4:-192.168.2.54}"
MAIL_RELAY_CT_ID="${MAIL_RELAY_CT_ID:-102}"

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
CONFIG_DIR="$HOME/.config/homelab-iac"
PVE_ENV_FILE="$CONFIG_DIR/proxmox.env"
MAIL_ENV_FILE="$CONFIG_DIR/mail-relay.env"
CT_SSH_KEY="$HOME/.ssh/proxmox-automation"
PVE_ROOT_SSH_KEY="$HOME/.ssh/proxmox-root"
TF_SOURCE_DIR="$REPO_ROOT/IaC/terraform/proxmox/mail-relay"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
STATE_DIR="$HOME/.local/state/homelab-iac/mail-relay-01/terraform"
WORK_DIR="${RUNNER_TEMP:-/tmp}/mail-relay-01-${MAIL_RELAY_CT_ID}"

PVE_ENDPOINT="https://192.168.2.70:8006/"
PVE_NODE_NAME="PROXMOX"
PVE_SSH_HOST="192.168.2.70"
ROOTFS_DATASTORE="vm-ssd"
TEMPLATE_FILE_ID="local:vztmpl/debian-13-standard_13.6-1_amd64.tar.zst"

for cmd in terraform ansible-playbook jq ssh python3; do
  command -v "$cmd" >/dev/null 2>&1 || die "Required command not found: $cmd"
done

[ -r "$PVE_ENV_FILE" ] || die "Missing Proxmox credential file: $PVE_ENV_FILE"
[ -r "$MAIL_ENV_FILE" ] || die "Missing mail relay config file: $MAIL_ENV_FILE"
[ -r "$CT_SSH_KEY" ] || die "Missing CT SSH key: $CT_SSH_KEY"
[ -r "$CT_SSH_KEY.pub" ] || die "Missing CT SSH public key: $CT_SSH_KEY.pub"
[ -r "$PVE_ROOT_SSH_KEY" ] || die "Missing Proxmox root SSH key: $PVE_ROOT_SSH_KEY"

. "$PVE_ENV_FILE"
. "$MAIL_ENV_FILE"

: "${TF_VAR_proxmox_api_token:?TF_VAR_proxmox_api_token missing from Proxmox credential file}"
: "${GMAIL_SMTP_USERNAME:?GMAIL_SMTP_USERNAME missing from mail relay config file}"
: "${GMAIL_APP_PASSWORD:?GMAIL_APP_PASSWORD missing from mail relay config file}"

export TF_VAR_proxmox_api_token
export GMAIL_SMTP_USERNAME
export GMAIL_APP_PASSWORD

MAIL_RELAY_HOSTNAME="$MAIL_RELAY_HOSTNAME" MAIL_RELAY_IPV4="$MAIL_RELAY_IPV4" MAIL_RELAY_CT_ID="$MAIL_RELAY_CT_ID"   bash "$REPO_ROOT/IaC/scripts/preflight-mail-relay.sh"   || die "Mail relay preflight failed"

[ ! -e "$STATE_DIR/terraform.tfstate" ] || die "Mail relay Terraform state already exists"

mkdir -p "$STATE_DIR" "$WORK_DIR"
cp "$TF_SOURCE_DIR"/*.tf "$STATE_DIR/"

export TF_VAR_proxmox_endpoint="$PVE_ENDPOINT"
export TF_VAR_proxmox_node_name="$PVE_NODE_NAME"
export TF_VAR_vm_id="$MAIL_RELAY_CT_ID"
export TF_VAR_hostname="$MAIL_RELAY_HOSTNAME"
export TF_VAR_ipv4_cidr="$MAIL_RELAY_IPV4/24"
export TF_VAR_rootfs_datastore_id="$ROOTFS_DATASTORE"
export TF_VAR_template_file_id="$TEMPLATE_FILE_ID"
export TF_VAR_protect_after_build=false
export TF_VAR_ssh_public_keys
TF_VAR_ssh_public_keys="$(jq -n --arg key "$(cat "$CT_SSH_KEY.pub")" '[$key]')"

CREATE_PLAN="$WORK_DIR/create.tfplan"
INVENTORY_FILE="$WORK_DIR/inventory.yml"

printf '===== TERRAFORM CREATE =====\n'
terraform -chdir="$STATE_DIR" init -input=false || die "Terraform init failed"
terraform -chdir="$STATE_DIR" validate || die "Terraform validation failed"
terraform -chdir="$STATE_DIR" plan -input=false -out="$CREATE_PLAN" || die "Terraform plan failed"

terraform -chdir="$STATE_DIR" show -json "$CREATE_PLAN" | jq -e '
  [.resource_changes[] | select(.change.actions != ["no-op"])] as $changes
  | ($changes | length) == 1
    and $changes[0].address == "proxmox_virtual_environment_container.mail_relay"
    and $changes[0].change.actions == ["create"]
' >/dev/null || die "Unexpected Terraform changes"

terraform -chdir="$STATE_DIR" apply -input=false "$CREATE_PLAN" || die "Terraform apply failed"

printf '\n===== ENABLE DEBIAN 13 LXC NESTING =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_SSH_HOST"   "pct set '$MAIL_RELAY_CT_ID' -features nesting=1 && (pct shutdown '$MAIL_RELAY_CT_ID' --timeout 30 || pct stop '$MAIL_RELAY_CT_ID') && pct start '$MAIL_RELAY_CT_ID'"   || die "LXC nesting bootstrap failed"

printf '\n===== WAIT FOR SSH =====\n'
ssh-keygen -R "$MAIL_RELAY_IPV4" >/dev/null 2>&1 || true
READY=0
for attempt in $(seq 1 30); do
  if ssh -i "$CT_SSH_KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new       -o ConnectTimeout=3 "root@$MAIL_RELAY_IPV4" true >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 4
done
[ "$READY" -eq 1 ] || die "mail-relay-01 SSH did not become ready"

cat > "$INVENTORY_FILE" <<EOF
---
all:
  children:
    mail_relay:
      hosts:
        $MAIL_RELAY_HOSTNAME:
          ansible_host: $MAIL_RELAY_IPV4
          ansible_user: root
          ansible_ssh_private_key_file: $CT_SSH_KEY
          homelab_tags: [homelab, iac, core, mail, smtp]
          homelab_comment: "Internal SMTP relay for homelab notifications via Gmail"
EOF

printf '\n===== ANSIBLE FIRST APPLY =====\n'
cd "$ANSIBLE_DIR"
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles"   ansible-playbook -i "$INVENTORY_FILE" playbooks/mail-relay.yml   || die "Mail relay Ansible configuration failed"

printf '\n===== ANSIBLE IDEMPOTENCE =====\n'
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles"   ansible-playbook -i "$INVENTORY_FILE" playbooks/mail-relay.yml   || die "Mail relay Ansible idempotence run failed"

printf '\n===== SMTP LISTENER CHECK =====\n'
python3 - "$MAIL_RELAY_IPV4" <<'PY'
import socket, sys
host=sys.argv[1]
with socket.create_connection((host,25),5) as s:
    banner=s.recv(512).decode("ascii","replace").strip()
    if not banner.startswith("220 "):
        raise SystemExit(f"unexpected SMTP banner: {banner}")
print("smtp_listener=PASS")
PY

printf '\n===== RESULT: BUILD PASS =====\n'
printf '%s (%s), CT %s on PROXMOX, is built and Postfix is configured.\n'   "$MAIL_RELAY_HOSTNAME" "$MAIL_RELAY_IPV4" "$MAIL_RELAY_CT_ID"
printf 'Outbound Gmail delivery, DNS publication, monitoring registration and final protection remain validation gates.\n'
