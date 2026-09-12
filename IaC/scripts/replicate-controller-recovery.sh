#!/usr/bin/env bash

SOURCE_ROOT="${HOME}/.local/share/homelab-recovery"
SSH_KEY="${HOME}/.ssh/proxmox-automation"
REMOTE_ROOT=".local/share/homelab-recovery/admin-01"

echo "===== CONTROLLER RECOVERY REPLICATION ====="

if [ ! -d "$SOURCE_ROOT" ]; then
    echo "STOP: source recovery directory missing"
    exit 1
fi

if [ ! -r "$SSH_KEY" ]; then
    echo "STOP: SSH key missing"
    exit 1
fi

BUNDLE="$(
    find "$SOURCE_ROOT" \
      -maxdepth 1 \
      -type f \
      -name 'controller-recovery-*.tar.gz.age' \
      -printf '%T@ %p\n' |
    sort -nr |
    head -1 |
    cut -d' ' -f2-
)"

if [ -z "$BUNDLE" ]; then
    echo "STOP: controller recovery bundle not found"
    exit 1
fi

MANIFEST="${BUNDLE%.tar.gz.age}.manifest.txt"

BOOTSTRAP="$(
    find "$SOURCE_ROOT" \
      -maxdepth 1 \
      -type f \
      -name 'age-key-bootstrap-*.txt.age' \
      -printf '%T@ %p\n' |
    sort -nr |
    head -1 |
    cut -d' ' -f2-
)"

if [ ! -s "$MANIFEST" ]; then
    echo "STOP: matching manifest missing"
    exit 1
fi

if [ ! -s "$BOOTSTRAP" ]; then
    echo "STOP: age-key bootstrap missing"
    exit 1
fi

echo
echo "===== SOURCE ====="

hostname
printf 'bundle=%s\n' "$(basename "$BUNDLE")"
printf 'manifest=%s\n' "$(basename "$MANIFEST")"
printf 'bootstrap=%s\n' "$(basename "$BOOTSTRAP")"

echo
echo "Checksums:"

sha256sum \
    "$BUNDLE" \
    "$MANIFEST" \
    "$BOOTSTRAP"

SOURCE_BUNDLE_SHA="$(sha256sum "$BUNDLE" | awk '{print $1}')"
SOURCE_MANIFEST_SHA="$(sha256sum "$MANIFEST" | awk '{print $1}')"
SOURCE_BOOTSTRAP_SHA="$(sha256sum "$BOOTSTRAP" | awk '{print $1}')"

RESULT=0

for TARGET in \
    "docker-01:192.168.2.220" \
    "media-01:192.168.2.195"
do
    NAME="${TARGET%%:*}"
    HOST="${TARGET##*:}"

    echo
    echo "############################################################"
    echo "$NAME ($HOST)"
    echo "############################################################"

    ssh \
      -i "$SSH_KEY" \
      -o BatchMode=yes \
      -o ConnectTimeout=10 \
      "james@$HOST" \
      "mkdir -p \"\$HOME/$REMOTE_ROOT\" &&
       chmod 700 \"\$HOME/.local/share/homelab-recovery\" &&
       chmod 700 \"\$HOME/$REMOTE_ROOT\" &&
       printf 'hostname=' &&
       hostname &&
       df -h \"\$HOME/$REMOTE_ROOT\""

    RC=$?

    if [ "$RC" -ne 0 ]; then
        echo "$NAME: destination_preflight=FAIL"
        RESULT=1
        continue
    fi

    echo
    echo "Copying..."

    scp \
      -i "$SSH_KEY" \
      -o BatchMode=yes \
      -p \
      "$BUNDLE" \
      "$MANIFEST" \
      "$BOOTSTRAP" \
      "james@$HOST:$REMOTE_ROOT/"

    RC=$?

    if [ "$RC" -ne 0 ]; then
        echo "$NAME: copy=FAIL"
        RESULT=1
        continue
    fi

    echo "$NAME: copy=PASS"

    REMOTE_RESULT="$(
        ssh \
          -i "$SSH_KEY" \
          -o BatchMode=yes \
          "james@$HOST" \
          "chmod 600 \"\$HOME/$REMOTE_ROOT\"/* &&
           sha256sum \
             \"\$HOME/$REMOTE_ROOT/$(basename "$BUNDLE")\" \
             \"\$HOME/$REMOTE_ROOT/$(basename "$MANIFEST")\" \
             \"\$HOME/$REMOTE_ROOT/$(basename "$BOOTSTRAP")\""
    )"

    printf '%s\n' "$REMOTE_RESULT"

    REMOTE_BUNDLE_SHA="$(printf '%s\n' "$REMOTE_RESULT" | sed -n '1s/[[:space:]].*//p')"
    REMOTE_MANIFEST_SHA="$(printf '%s\n' "$REMOTE_RESULT" | sed -n '2s/[[:space:]].*//p')"
    REMOTE_BOOTSTRAP_SHA="$(printf '%s\n' "$REMOTE_RESULT" | sed -n '3s/[[:space:]].*//p')"

    if [ "$REMOTE_BUNDLE_SHA" = "$SOURCE_BUNDLE_SHA" ] &&
       [ "$REMOTE_MANIFEST_SHA" = "$SOURCE_MANIFEST_SHA" ] &&
       [ "$REMOTE_BOOTSTRAP_SHA" = "$SOURCE_BOOTSTRAP_SHA" ]; then
        echo "$NAME: checksum_validation=PASS"
    else
        echo "$NAME: checksum_validation=FAIL"
        RESULT=1
    fi
done

echo
echo "############################################################"
echo "Proxmox-2 (192.168.2.71)"
echo "############################################################"

PVE2_HOST="192.168.2.71"
PVE2_KEY="${HOME}/.ssh/proxmox-root"
PVE2_ROOT="/var/lib/homelab-recovery/admin-01"

ssh \
  -i "$PVE2_KEY" \
  -o BatchMode=yes \
  -o ConnectTimeout=10 \
  "root@$PVE2_HOST" \
  "install -d -m 700 '$PVE2_ROOT'"

RC=$?

if [ "$RC" -ne 0 ]; then
    echo "Proxmox-2: destination_preflight=FAIL"
    RESULT=1
else
    scp \
      -i "$PVE2_KEY" \
      -o BatchMode=yes \
      -p \
      "$BUNDLE" \
      "$MANIFEST" \
      "$BOOTSTRAP" \
      "root@$PVE2_HOST:$PVE2_ROOT/"

    RC=$?

    if [ "$RC" -ne 0 ]; then
        echo "Proxmox-2: copy=FAIL"
        RESULT=1
    else
        echo "Proxmox-2: copy=PASS"

        REMOTE_RESULT="$(
            ssh \
              -i "$PVE2_KEY" \
              -o BatchMode=yes \
              "root@$PVE2_HOST" \
              "chmod 600 '$PVE2_ROOT'/* &&
               sha256sum \
                 '$PVE2_ROOT/$(basename "$BUNDLE")' \
                 '$PVE2_ROOT/$(basename "$MANIFEST")' \
                 '$PVE2_ROOT/$(basename "$BOOTSTRAP")'"
        )"

        printf '%s\n' "$REMOTE_RESULT"

        REMOTE_BUNDLE_SHA="$(
            printf '%s\n' "$REMOTE_RESULT" |
            sed -n '1s/[[:space:]].*//p'
        )"

        REMOTE_MANIFEST_SHA="$(
            printf '%s\n' "$REMOTE_RESULT" |
            sed -n '2s/[[:space:]].*//p'
        )"

        REMOTE_BOOTSTRAP_SHA="$(
            printf '%s\n' "$REMOTE_RESULT" |
            sed -n '3s/[[:space:]].*//p'
        )"

        if [ "$REMOTE_BUNDLE_SHA" = "$SOURCE_BUNDLE_SHA" ] &&
           [ "$REMOTE_MANIFEST_SHA" = "$SOURCE_MANIFEST_SHA" ] &&
           [ "$REMOTE_BOOTSTRAP_SHA" = "$SOURCE_BOOTSTRAP_SHA" ]; then
            echo "Proxmox-2: checksum_validation=PASS"
        else
            echo "Proxmox-2: checksum_validation=FAIL"
            RESULT=1
        fi
    fi
fi


echo
echo "===== RESULT ====="

if [ "$RESULT" -eq 0 ]; then
    echo "admin-01=PASS"
    echo "docker-01=PASS"
    echo "media-01=PASS"
    echo "result=PASS"
else
    echo "result=FAIL"
fi

exit "$RESULT"
