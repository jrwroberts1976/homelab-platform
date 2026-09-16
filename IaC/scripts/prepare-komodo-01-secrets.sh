#!/usr/bin/env bash

set -u

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

command -v openssl >/dev/null 2>&1 ||
  die "openssl is required"

CONFIG_DIR="$HOME/.config/homelab-iac"
ENV_FILE="$CONFIG_DIR/komodo-01.env"

mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"

if [ -e "$ENV_FILE" ]; then
  die "$ENV_FILE already exists; refusing to overwrite Komodo credentials"
fi

printf 'Komodo initial admin username [james]: '
IFS= read -r ADMIN_USER
ADMIN_USER="${ADMIN_USER:-james}"

[ "${#ADMIN_USER}" -ge 3 ] ||
  die "Komodo admin username is too short"

printf 'Komodo initial admin password (minimum 16 characters): '
IFS= read -rs ADMIN_PASSWORD
printf '\n'

[ "${#ADMIN_PASSWORD}" -ge 16 ] ||
  die "Komodo admin password is too short"

printf 'Confirm Komodo initial admin password: '
IFS= read -rs ADMIN_PASSWORD_CONFIRM
printf '\n'

[ "$ADMIN_PASSWORD" = "$ADMIN_PASSWORD_CONFIRM" ] ||
  die "Passwords do not match"

DATABASE_PASSWORD="$(openssl rand -hex 32)" ||
  die "Failed to generate MongoDB password"

JWT_SECRET="$(openssl rand -hex 32)" ||
  die "Failed to generate JWT secret"

WEBHOOK_SECRET="$(openssl rand -hex 32)" ||
  die "Failed to generate webhook secret"

umask 077

{
  printf 'export KOMODO_INIT_ADMIN_USERNAME=%q\n' "$ADMIN_USER"
  printf 'export KOMODO_INIT_ADMIN_PASSWORD=%q\n' "$ADMIN_PASSWORD"
  printf 'export KOMODO_DATABASE_PASSWORD=%q\n' "$DATABASE_PASSWORD"
  printf 'export KOMODO_JWT_SECRET=%q\n' "$JWT_SECRET"
  printf 'export KOMODO_WEBHOOK_SECRET=%q\n' "$WEBHOOK_SECRET"
} > "$ENV_FILE"

chmod 600 "$ENV_FILE"

unset \
  ADMIN_PASSWORD \
  ADMIN_PASSWORD_CONFIRM \
  DATABASE_PASSWORD \
  JWT_SECRET \
  WEBHOOK_SECRET

printf 'komodo_secret_file=%s\n' "$ENV_FILE"
printf 'permissions='
stat -c '%a' "$ENV_FILE"
printf 'Secrets stored without printing their values.\n'
