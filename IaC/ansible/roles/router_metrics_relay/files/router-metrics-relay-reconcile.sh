#!/bin/bash
set -euo pipefail

COMPOSE=/opt/homelab-router-metrics-relay/docker-compose.yml
PROJECT=router-metrics-relay
SERVICE=router-metrics-relay

# Never manipulate Prometheus itself.
if ! systemctl -q is-active router-metrics-tunnel.service ||
   ! systemctl -q is-active router-metrics-relay.service; then
    echo "Host relay services unavailable; skipping"
    exit 0
fi

if ! test -S /run/router-metrics-relay/metrics.sock; then
    echo "Host relay socket unavailable; skipping"
    exit 0
fi

prom_id=$(docker inspect \
    --format '{{.Id}}' monitoring-prometheus-1 2>/dev/null) || exit 0

prom_running=$(docker inspect \
    --format '{{.State.Running}}' monitoring-prometheus-1)

if [[ "$prom_running" != "true" ]]; then
    echo "Prometheus not running; skipping"
    exit 0
fi

relay_id=$(docker inspect \
    --format '{{.Id}}' "$SERVICE" 2>/dev/null) || relay_id=""

if [[ -n "$relay_id" ]]; then
    relay_running=$(docker inspect \
        --format '{{.State.Running}}' "$SERVICE")

    relay_network=$(docker inspect \
        --format '{{.HostConfig.NetworkMode}}' "$SERVICE")

    if [[ "$relay_running" == "true" &&
          "$relay_network" == "container:$prom_id" ]]; then
        prom_pid=$(docker inspect             --format '{{.State.Pid}}' monitoring-prometheus-1)

        if [[ "$prom_pid" =~ ^[0-9]+$ ]] &&
           (( prom_pid > 1 )) &&
           nsenter -t "$prom_pid" -n              curl --fail --silent --max-time 5              --output /dev/null              http://127.0.0.1:19101/metrics; then
            echo "RELAY_RECONCILIATION=HEALTHY"
            exit 0
        fi

        echo "RELAY_RECONCILIATION=DEGRADED"
        exit 0
    fi
fi

echo "Relay missing, stopped or attached to old Prometheus namespace"

docker compose \
    -p "$PROJECT" \
    -f "$COMPOSE" \
    up -d --no-deps --force-recreate "$SERVICE"

echo "RELAY_RECONCILIATION=RECOVERED"
