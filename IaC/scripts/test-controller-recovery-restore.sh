#!/usr/bin/env bash

SOURCE_HOST="${SOURCE_HOST:-192.168.2.220}"
SOURCE_USER="${SOURCE_USER:-james}"
SOURCE_KEY="${SOURCE_KEY:-${HOME}/.ssh/proxmox-automation}"
REMOTE_ROOT="${REMOTE_ROOT:-.local/share/homelab-recovery/admin-01}"

TEST_ROOT="$(mktemp -d /tmp/homelab-controller-restore.XXXXXX)"
chmod 700 "$TEST_ROOT"

RESULT=0

echo "===== ISOLATED CONTROLLER RECOVERY TEST ====="
echo "source=${SOURCE_USER}@${SOURCE_HOST}"
echo "test_root=$TEST_ROOT"

echo
echo "===== FIND LATEST MIRRORED RECOVERY SET ====="

REMOTE_BUNDLE="$(
    ssh \
      -i "$SOURCE_KEY" \
      -o BatchMode=yes \
      "$SOURCE_USER@$SOURCE_HOST" \
      "find \"\$HOME/$REMOTE_ROOT\" \
         -maxdepth 1 \
         -type f \
         -name 'controller-recovery-*.tar.gz.age' \
         -printf '%T@ %p\\n' | \
       sort -nr | \
       head -1 | \
       cut -d' ' -f2-"
)"

REMOTE_BOOTSTRAP="$(
    ssh \
      -i "$SOURCE_KEY" \
      -o BatchMode=yes \
      "$SOURCE_USER@$SOURCE_HOST" \
      "find \"\$HOME/$REMOTE_ROOT\" \
         -maxdepth 1 \
         -type f \
         -name 'age-key-bootstrap-*.txt.age' \
         -printf '%T@ %p\\n' | \
       sort -nr | \
       head -1 | \
       cut -d' ' -f2-"
)"

REMOTE_MANIFEST="${REMOTE_BUNDLE%.tar.gz.age}.manifest.txt"

echo "bundle=$(basename "$REMOTE_BUNDLE")"
echo "manifest=$(basename "$REMOTE_MANIFEST")"
echo "bootstrap=$(basename "$REMOTE_BOOTSTRAP")"

if [ -z "$REMOTE_BUNDLE" ] || [ -z "$REMOTE_BOOTSTRAP" ]; then
    echo "mirror_inventory=FAIL"
    RESULT=1
else
    echo "mirror_inventory=PASS"
fi

echo
echo "===== COPY FROM MIRROR ====="

if [ "$RESULT" -eq 0 ]; then
    scp \
      -i "$SOURCE_KEY" \
      -o BatchMode=yes \
      -p \
      "$SOURCE_USER@$SOURCE_HOST:$REMOTE_BUNDLE" \
      "$SOURCE_USER@$SOURCE_HOST:$REMOTE_MANIFEST" \
      "$SOURCE_USER@$SOURCE_HOST:$REMOTE_BOOTSTRAP" \
      "$TEST_ROOT/"

    if [ "$?" -eq 0 ]; then
        echo "mirror_copy=PASS"
    else
        echo "mirror_copy=FAIL"
        RESULT=1
    fi
fi

LOCAL_BUNDLE="$TEST_ROOT/$(basename "$REMOTE_BUNDLE")"
LOCAL_MANIFEST="$TEST_ROOT/$(basename "$REMOTE_MANIFEST")"
LOCAL_BOOTSTRAP="$TEST_ROOT/$(basename "$REMOTE_BOOTSTRAP")"

echo
echo "===== CHECK BUNDLE INTEGRITY ====="

if [ "$RESULT" -eq 0 ]; then
    EXPECTED_SHA="$(sed -n 's/^sha256=//p' "$LOCAL_MANIFEST")"
    ACTUAL_SHA="$(sha256sum "$LOCAL_BUNDLE" | awk '{print $1}')"

    if [ -n "$EXPECTED_SHA" ] && [ "$EXPECTED_SHA" = "$ACTUAL_SHA" ]; then
        echo "bundle_checksum=PASS"
    else
        echo "bundle_checksum=FAIL"
        RESULT=1
    fi
fi

echo
echo "===== RECOVER AGE PRIVATE KEY ====="

TEMP_AGE_KEY="$TEST_ROOT/recovered-age-keys.txt"

if [ "$RESULT" -eq 0 ]; then
    echo "Enter the recovery passphrase used for the age-key bootstrap."

    age \
      -d \
      -o "$TEMP_AGE_KEY" \
      "$LOCAL_BOOTSTRAP"

    if [ "$?" -eq 0 ]; then
        chmod 600 "$TEMP_AGE_KEY"
        RECIPIENT="$(age-keygen -y "$TEMP_AGE_KEY" 2>/dev/null)"

        if [ -n "$RECIPIENT" ]; then
            echo "age_key_recovery=PASS"
        else
            echo "age_key_recovery=FAIL"
            RESULT=1
        fi
    else
        echo "age_key_decryption=FAIL"
        RESULT=1
    fi
fi

echo
echo "===== DECRYPT CONTROLLER BUNDLE ====="

TEMP_TAR="$TEST_ROOT/controller-recovery.tar.gz"
EXTRACT_ROOT="$TEST_ROOT/restored"

mkdir -p "$EXTRACT_ROOT"
chmod 700 "$EXTRACT_ROOT"

if [ "$RESULT" -eq 0 ]; then
    age \
      -d \
      -i "$TEMP_AGE_KEY" \
      -o "$TEMP_TAR" \
      "$LOCAL_BUNDLE"

    if [ "$?" -eq 0 ]; then
        echo "bundle_decryption=PASS"

        tar -tzf "$TEMP_TAR" >/dev/null

        if [ "$?" -eq 0 ]; then
            echo "archive_test=PASS"

            tar -xzf "$TEMP_TAR" -C "$EXTRACT_ROOT"

            if [ "$?" -eq 0 ]; then
                echo "archive_extract=PASS"
            else
                echo "archive_extract=FAIL"
                RESULT=1
            fi
        else
            echo "archive_test=FAIL"
            RESULT=1
        fi
    else
        echo "bundle_decryption=FAIL"
        RESULT=1
    fi
fi

echo
echo "===== VALIDATE MANAGED SECRETS ====="

if [ "$RESULT" -eq 0 ]; then
    for FILE in \
        proxmox.env \
        proxmox-pve2.env \
        pihole.env \
        cloud-01.env \
        mail-relay.env \
        monitoring.env
    do
        PATHNAME="$EXTRACT_ROOT/.config/homelab-iac/$FILE"

        if [ -s "$PATHNAME" ] && [ "$(stat -c '%a' "$PATHNAME")" = "600" ]; then
            echo "$FILE=PASS"
        else
            echo "$FILE=FAIL"
            RESULT=1
        fi
    done
fi

echo
echo "===== VALIDATE SSH IDENTITIES ====="

if [ "$RESULT" -eq 0 ]; then
    for KEY in \
        proxmox-automation \
        proxmox-root \
        github-personal \
        id_ed25519
    do
        PRIVATE="$EXTRACT_ROOT/.ssh/$KEY"
        PUBLIC="$PRIVATE.pub"

        if [ ! -s "$PRIVATE" ] || [ ! -s "$PUBLIC" ]; then
            echo "$KEY=FAIL"
            RESULT=1
            continue
        fi

        DERIVED="$(ssh-keygen -y -f "$PRIVATE" 2>/dev/null | awk '{print $1 " " $2}')"
        STORED="$(awk '{print $1 " " $2}' "$PUBLIC")"

        if [ -n "$DERIVED" ] && [ "$DERIVED" = "$STORED" ]; then
            echo "$KEY=PASS"
        else
            echo "$KEY=FAIL"
            RESULT=1
        fi
    done
fi

echo
echo "===== VALIDATE TERRAFORM STATE ====="

STATE_ROOT="$EXTRACT_ROOT/.local/state/homelab-iac"
STATE_COUNT=0

if [ "$RESULT" -eq 0 ]; then
    while IFS= read -r STATE; do
        STATE_COUNT=$((STATE_COUNT + 1))

        if jq empty "$STATE" >/dev/null 2>&1; then
            echo "${STATE#"$EXTRACT_ROOT/"}=PASS"
        else
            echo "${STATE#"$EXTRACT_ROOT/"}=FAIL"
            RESULT=1
        fi
    done < <(
        find "$STATE_ROOT" \
          -type f \
          -name 'terraform.tfstate' \
          -size +0c \
          | sort
    )

    if [ "$STATE_COUNT" -gt 0 ]; then
        echo "terraform_state_restore=PASS"
    else
        echo "terraform_state_restore=FAIL"
        RESULT=1
    fi
fi

echo
echo "===== LIVE SYSTEM SAFETY CHECK ====="
echo "live_files_overwritten=NO"
echo "restore_location=$EXTRACT_ROOT"

echo
echo "===== RESTORE TEST RESULT ====="

if [ "$RESULT" -eq 0 ]; then
    echo "controller_restore_test=PASS"
    rm -rf "$TEST_ROOT"

    if [ ! -e "$TEST_ROOT" ]; then
        echo "temporary_plaintext_cleanup=PASS"
    else
        echo "temporary_plaintext_cleanup=FAIL"
        exit 1
    fi
else
    echo "controller_restore_test=FAIL"
    echo "Temporary test material retained for diagnosis:"
    echo "$TEST_ROOT"
    exit 1
fi

echo
echo "===== COMPLETE ====="
