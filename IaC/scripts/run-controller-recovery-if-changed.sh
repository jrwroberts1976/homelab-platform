#!/usr/bin/env bash

HOME_DIR="${HOME}"
RECOVERY_ROOT="${HOME_DIR}/.local/share/homelab-recovery"
FINGERPRINT_FILE="${RECOVERY_ROOT}/.controller-recovery-source.sha256"

CREATE_SCRIPT="${HOME_DIR}/.local/bin/create-controller-recovery-bundle.sh"
REPLICATE_SCRIPT="${HOME_DIR}/.local/bin/replicate-controller-recovery.sh"

mkdir -p "$RECOVERY_ROOT"
chmod 700 "$RECOVERY_ROOT"

TMP="$(mktemp "${RECOVERY_ROOT}/.fingerprint.XXXXXX")"
chmod 600 "$TMP"

fingerprint_file() {
    FILE="$1"
    LABEL="$2"

    if [ ! -f "$FILE" ]; then
        printf 'MISSING\t%s\n' "$LABEL"
        return
    fi

    printf 'FILE\t%s\t%s\t' \
        "$LABEL" \
        "$(stat -c '%a' "$FILE")"

    sha256sum "$FILE" |
    awk '{print $1}'
}

{
    echo "===== MANAGED SECRETS ====="

    find \
      "$HOME_DIR/.config/homelab-iac" \
      -type f \
      -print0 2>/dev/null |
    sort -z |
    while IFS= read -r -d '' FILE; do
        REL="${FILE#"$HOME_DIR/"}"
        fingerprint_file "$FILE" "$REL"
    done

    echo "===== TERRAFORM STATE ====="

    find \
      "$HOME_DIR/.local/state/homelab-iac" \
      -type f \
      \( \
        -name 'terraform.tfstate' \
        -o \
        -name 'terraform.tfstate.backup' \
      \) \
      -print0 2>/dev/null |
    sort -z |
    while IFS= read -r -d '' FILE; do
        REL="${FILE#"$HOME_DIR/"}"
        fingerprint_file "$FILE" "$REL"
    done

    echo "===== SSH RECOVERY MATERIAL ====="

    for REL in \
        ".ssh/config" \
        ".ssh/authorized_keys" \
        ".ssh/proxmox-automation" \
        ".ssh/proxmox-automation.pub" \
        ".ssh/proxmox-root" \
        ".ssh/proxmox-root.pub" \
        ".ssh/github-personal" \
        ".ssh/github-personal.pub" \
        ".ssh/id_ed25519" \
        ".ssh/id_ed25519.pub"
    do
        fingerprint_file \
          "$HOME_DIR/$REL" \
          "$REL"
    done
} |
sha256sum |
awk '{print $1}' > "$TMP"

NEW_FINGERPRINT="$(cat "$TMP")"

OLD_FINGERPRINT=""

if [ -r "$FINGERPRINT_FILE" ]; then
    OLD_FINGERPRINT="$(
        tr -d '[:space:]' < "$FINGERPRINT_FILE"
    )"
fi

LATEST_BUNDLE="$(
    find "$RECOVERY_ROOT" \
      -maxdepth 1 \
      -type f \
      -name 'controller-recovery-*.tar.gz.age' \
      -printf '%T@ %p\n' |
    sort -nr |
    head -1 |
    cut -d' ' -f2-
)"

echo "new_fingerprint=$NEW_FINGERPRINT"
echo "old_fingerprint=${OLD_FINGERPRINT:-NONE}"

if [ -n "$OLD_FINGERPRINT" ] &&
   [ "$NEW_FINGERPRINT" = "$OLD_FINGERPRINT" ] &&
   [ -s "$LATEST_BUNDLE" ]
then
    rm -f "$TMP"

    echo "change_detected=NO"
    echo "new_bundle=NO"
    echo "result=NO_CHANGE"

    exit 0
fi

echo "change_detected=YES"

"$CREATE_SCRIPT"

RC=$?

if [ "$RC" -ne 0 ]; then
    rm -f "$TMP"
    echo "result=CREATE_FAILED"
    exit "$RC"
fi

"$REPLICATE_SCRIPT"

RC=$?

if [ "$RC" -ne 0 ]; then
    rm -f "$TMP"
    echo "result=REPLICATION_FAILED"
    exit "$RC"
fi

mv "$TMP" "$FINGERPRINT_FILE"
chmod 600 "$FINGERPRINT_FILE"

echo "fingerprint_committed=YES"
echo "result=PASS"
