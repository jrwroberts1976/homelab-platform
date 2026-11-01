#!/usr/bin/env bash
# Called by one-shot systemd timer; never alters kernel QoS.
set -euo pipefail
[[ $EUID -eq 0 && "$(hostname -s)" == raspberrypi ]] || exit 2
MARKER=/run/router-qos-download-cutover.pending
RESTORE=/usr/local/libexec/router-qos-download-cutover/rollback-watchdog.sh
# No marker means no cutover: no action. Symlink marker must not be trusted.
[[ ! -L "$MARKER" ]] || { echo "REFUSE: symlink marker"; exit 2; }
[[ -e "$MARKER" ]] || { echo "SKIP: cutover not armed"; exit 0; }
[[ -f "$MARKER" ]] || { echo "REFUSE: invalid marker type"; exit 2; }
# The only permitted action is to restore known legacy entrypoints.
"$RESTORE" restore
echo "ROLLBACK: unconfirmed cutover; legacy entrypoints restored"
