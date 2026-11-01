#!/bin/bash
set -euo pipefail

COMPOSE=/opt/homelab-router-metrics-relay/docker-compose.yml
PROJECT=router-metrics-relay
SERVICE=router-metrics-relay
PROMETHEUS=monitoring-prometheus-1
SOCKET=/run/router-metrics-relay/metrics.sock
COOLDOWN_FILE=/run/router-metrics-reconcile/last-recreate
COOLDOWN_SECONDS=300

# Never change Prometheus, the router, or its SSH tunnel.
if ! systemctl -q is-active router-metrics-tunnel.service ||
   ! systemctl -q is-active router-metrics-relay.service; then
    echo "RELAY_RECONCILIATION=SKIPPED_HOST_SERVICES"
    exit 0
fi

if [[ ! -S "$SOCKET" ]]; then
    echo "RELAY_RECONCILIATION=SKIPPED_HOST_SOCKET"
    exit 0
fi

# A broken router/tunnel cannot be repaired by recreating the Docker relay.
if ! curl --fail --silent --max-time 5 --output /dev/null     http://127.0.0.1:19100/metrics; then
    echo "RELAY_RECONCILIATION=SKIPPED_UPSTREAM"
    exit 0
fi

prom_id=$(docker inspect --format '{{.Id}}' "$PROMETHEUS" 2>/dev/null) || exit 0
prom_running=$(docker inspect --format '{{.State.Running}}' "$PROMETHEUS")
if [[ "$prom_running" != "true" ]]; then
    echo "RELAY_RECONCILIATION=SKIPPED_PROMETHEUS"
    exit 0
fi

prom_pid=$(docker inspect --format '{{.State.Pid}}' "$PROMETHEUS")
if [[ ! "$prom_pid" =~ ^[0-9]+$ ]] || (( prom_pid <= 1 )); then
    echo "RELAY_RECONCILIATION=SKIPPED_PROMETHEUS_PID"
    exit 0
fi

healthy() {
    nsenter -t "$prom_pid" -n         curl --fail --silent --max-time 5 --output /dev/null         http://127.0.0.1:19101/metrics
}

relay_id=$(docker inspect --format '{{.Id}}' "$SERVICE" 2>/dev/null) || relay_id=""
if [[ -n "$relay_id" ]]; then
    relay_running=$(docker inspect --format '{{.State.Running}}' "$SERVICE")
    relay_network=$(docker inspect --format '{{.HostConfig.NetworkMode}}' "$SERVICE")
    if [[ "$relay_running" == "true" &&
          "$relay_network" == "container:$prom_id" ]] && healthy; then
        echo "RELAY_RECONCILIATION=HEALTHY"
        exit 0
    fi
fi

# Prevent a broken mount or permission issue causing a recreate every minute.
now=$(date +%s)
if [[ -f "$COOLDOWN_FILE" ]]; then
    last=$(cat "$COOLDOWN_FILE" 2>/dev/null || echo 0)
    if [[ "$last" =~ ^[0-9]+$ ]] && (( now >= last && now - last < COOLDOWN_SECONDS )); then
        echo "RELAY_RECONCILIATION=DEGRADED_COOLDOWN"
        exit 0
    fi
fi

echo "$now" > "$COOLDOWN_FILE"
echo "Recreating only $SERVICE to refresh Docker mount/network attachment"
docker compose -p "$PROJECT" -f "$COMPOSE"     up -d --no-deps --force-recreate "$SERVICE"

for attempt in 1 2 3 4 5; do
    if healthy; then
        echo "RELAY_RECONCILIATION=RECOVERED"
        exit 0
    fi
    sleep 2
done
echo "RELAY_RECONCILIATION=DEGRADED_AFTER_RECREATE" >&2
exit 1
