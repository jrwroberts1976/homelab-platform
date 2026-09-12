#!/usr/bin/env bash

HOME_DIR="${HOME}"
AGE_KEY="${HOME_DIR}/.config/sops/age/keys.txt"
OUTPUT_ROOT="${HOME_DIR}/.local/share/homelab-recovery"

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BUNDLE="${OUTPUT_ROOT}/controller-recovery-${TIMESTAMP}.tar.gz.age"
MANIFEST="${OUTPUT_ROOT}/controller-recovery-${TIMESTAMP}.manifest.txt"

echo "===== CONTROLLER RECOVERY BUNDLE ====="

for CMD in age age-keygen tar sha256sum mktemp; do
    if ! command -v "$CMD" >/dev/null 2>&1; then
        echo "STOP: required command missing: $CMD"
        exit 1
    fi
done

if [ ! -r "$AGE_KEY" ]; then
    echo "STOP: age private key is not readable"
    exit 1
fi

REQUIRED_PATHS=(
    ".config/homelab-iac"
    ".local/state/homelab-iac"
    ".ssh/config"
    ".ssh/authorized_keys"
    ".ssh/proxmox-automation"
    ".ssh/proxmox-automation.pub"
    ".ssh/proxmox-root"
    ".ssh/proxmox-root.pub"
    ".ssh/github-personal"
    ".ssh/github-personal.pub"
    ".ssh/id_ed25519"
    ".ssh/id_ed25519.pub"
)

echo
echo "===== SOURCE PREFLIGHT ====="

MISSING=0

for ITEM in "${REQUIRED_PATHS[@]}"; do
    if [ -e "${HOME_DIR}/${ITEM}" ]; then
        printf 'PRESENT  %s\n' "$ITEM"
    else
        printf 'MISSING  %s\n' "$ITEM"
        MISSING=1
    fi
done

if [ "$MISSING" -ne 0 ]; then
    echo
    echo "STOP: required recovery material is missing"
    exit 1
fi

RECIPIENT="$(age-keygen -y "$AGE_KEY" 2>/dev/null)"

if [ -z "$RECIPIENT" ]; then
    echo "STOP: could not derive age recipient"
    exit 1
fi

mkdir -p "$OUTPUT_ROOT"
chmod 700 "$OUTPUT_ROOT"

TMP_TAR="$(mktemp "${OUTPUT_ROOT}/controller-recovery.XXXXXX.tar.gz")"
chmod 600 "$TMP_TAR"

echo
echo "===== CREATE PLAINTEXT TAR ====="

tar \
    -C "$HOME_DIR" \
    -czf "$TMP_TAR" \
    "${REQUIRED_PATHS[@]}"

RC=$?

if [ "$RC" -ne 0 ]; then
    echo "STOP: tar creation failed"
    rm -f "$TMP_TAR"
    exit 1
fi

echo "plaintext_tar=PASS"

echo
echo "===== ENCRYPT ====="

age \
    -r "$RECIPIENT" \
    -o "$BUNDLE" \
    "$TMP_TAR"

RC=$?

rm -f "$TMP_TAR"

if [ "$RC" -ne 0 ]; then
    echo "STOP: age encryption failed"
    rm -f "$BUNDLE"
    exit 1
fi

chmod 600 "$BUNDLE"

echo "encryption=PASS"

echo
echo "===== DECRYPTION VALIDATION ====="

age \
    -d \
    -i "$AGE_KEY" \
    "$BUNDLE" |
tar -tzf - >/dev/null

RC=$?

if [ "$RC" -ne 0 ]; then
    echo "STOP: encrypted bundle validation failed"
    exit 1
fi

echo "decrypt_test=PASS"

SHA256="$(sha256sum "$BUNDLE" | awk '{print $1}')"
SIZE="$(stat -c '%s' "$BUNDLE")"

{
    echo "Homelab controller recovery bundle"
    echo
    echo "created=${TIMESTAMP}"
    echo "host=$(hostname)"
    echo "bundle=$(basename "$BUNDLE")"
    echo "bytes=${SIZE}"
    echo "sha256=${SHA256}"
    echo "age_recipient=${RECIPIENT}"
    echo
    echo "Included:"
    for ITEM in "${REQUIRED_PATHS[@]}"; do
        echo "  ${ITEM}"
    done
    echo
    echo "Not included:"
    echo "  .config/sops/age/keys.txt"
    echo
    echo "The age private key requires a separate bootstrap backup."
} > "$MANIFEST"

chmod 600 "$MANIFEST"

echo
echo "===== RESULT ====="

stat -c '%A %U:%G %s bytes %n' \
    "$BUNDLE" \
    "$MANIFEST"

echo "sha256=$SHA256"
echo "decrypt_test=PASS"
echo "age_private_key_in_bundle=NO"
echo "result=PASS"
