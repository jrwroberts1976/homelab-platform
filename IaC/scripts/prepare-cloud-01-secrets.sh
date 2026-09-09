#!/usr/bin/env bash

set -u

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

command -v openssl >/dev/null 2>&1 || die "openssl is required"

CONFIG_DIR="$HOME/.config/homelab-iac"
ENV_FILE="$CONFIG_DIR/cloud-01.env"

mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"

if [ -e "$ENV_FILE" ]; then
  die "$ENV_FILE already exists; refusing to overwrite protected cloud credentials"
fi

printf 'Nextcloud admin username [james]: '
IFS= read -r ADMIN_USER
ADMIN_USER="${ADMIN_USER:-james}"

printf 'Nextcloud admin password (minimum 16 characters): '
IFS= read -rs ADMIN_PASSWORD
printf '\n'
[ "${#ADMIN_PASSWORD}" -ge 16 ] || die "Nextcloud admin password is too short"

printf 'Confirm Nextcloud admin password: '
IFS= read -rs ADMIN_PASSWORD_CONFIRM
printf '\n'
[ "$ADMIN_PASSWORD" = "$ADMIN_PASSWORD_CONFIRM" ] || die "Passwords do not match"

POSTGRES_PASSWORD="$(openssl rand -hex 32)" || die "Failed to generate PostgreSQL password"
REDIS_PASSWORD="$(openssl rand -hex 32)" || die "Failed to generate Redis password"

umask 077
{
  printf 'export NEXTCLOUD_ADMIN_USER=%q\n' "$ADMIN_USER"
  printf 'export NEXTCLOUD_ADMIN_PASSWORD=%q\n' "$ADMIN_PASSWORD"
  printf 'export CLOUD_POSTGRES_PASSWORD=%q\n' "$POSTGRES_PASSWORD"
  printf 'export CLOUD_REDIS_PASSWORD=%q\n' "$REDIS_PASSWORD"
} > "$ENV_FILE"

chmod 600 "$ENV_FILE"

unset ADMIN_PASSWORD ADMIN_PASSWORD_CONFIRM POSTGRES_PASSWORD REDIS_PASSWORD

printf 'cloud_secret_file=%s\n' "$ENV_FILE"
printf 'permissions='
stat -c '%a' "$ENV_FILE"
printf 'Secrets were generated/stored without printing their values.\n'
