#!/bin/bash
set -Eeuo pipefail

if [[ "${1:-}" != "APPROVE-LOOPBACK-CUTOVER" ]]; then
    echo "ERROR: Explicit cutover approval required"
    exit 1
fi

# This is a one-time migration, not a routine deployment tool.
if [[ -d /root/nextcloud-hardened-baseline-20261026 ]]; then
    echo "REFUSED: Hardened baseline exists; migration already completed"
    exit 1
fi

backup=/root/nextcloud-http-isolation-20261021
compose=/opt/cloud-01/docker-compose.yml
nginx=/etc/nginx/conf.d/nextcloud-https.conf
candidate="$backup/nextcloud-https.candidate.conf"
fqdn=nextcloud.home.jrwroberts.co.uk
armed=0

rollback() {
    rc=$?
    trap - ERR INT TERM
    set +e

    if [[ "$armed" == 1 ]]; then
        echo "===== ROLLBACK STARTED ====="

        install -m 0644 "$backup/docker-compose.yml" "$compose"
        install -m 0644 "$backup/nextcloud-https.conf" "$nginx"

        docker compose --project-directory /opt/cloud-01 \
            up -d --no-deps --pull never app

        nginx -t && systemctl reload nginx

        echo "===== ROLLBACK HEALTH ====="
        restored=0
        for attempt in $(seq 1 20); do
            if curl --noproxy "*" -fsS --max-time 8 --resolve "$fqdn:443:192.168.2.53" "https://$fqdn/status.php" >/dev/null 2>&1; then
                restored=1
                echo "PASS: HTTPS restored on attempt $attempt"
                break
            fi
            echo "Rollback check $attempt failed"
            sleep 3
        done
        if [[ "$restored" != 1 ]]; then
            echo "WARNING: Manual recovery required"
        fi
    else
        echo "Preflight failed; production not modified"
    fi

    exit "$((rc == 0 ? 1 : rc))"
}

trap rollback ERR INT TERM

echo "===== PREFLIGHT ====="

test -s "$backup/docker-compose.yml"
test -s "$backup/nextcloud-https.conf"
test -s "$candidate"

cmp -s "$nginx" "$backup/nextcloud-https.conf"

grep -Fq '"127.0.0.1:8080:80"' "$compose"
grep -Fq 'APACHE_DISABLE_REWRITE_IP: "1"' "$compose"
grep -Fq 'TRUSTED_PROXIES: "192.168.2.53 172.18.0.1"' "$compose"
grep -Fq 'proxy_pass http://127.0.0.1:8080;' "$candidate"

docker compose --project-directory /opt/cloud-01 config --quiet
nginx -t
systemctl is-active --quiet nginx

curl --noproxy "*" -fsS --max-time 15 \
    --resolve "$fqdn:443:192.168.2.53" \
    "https://$fqdn/status.php" >/dev/null

echo "PASS: Preflight complete"

echo "===== ACTIVATE LOOPBACK BACKEND ====="
armed=1

install -m 0644 "$candidate" "$nginx"
nginx -t

docker compose --project-directory /opt/cloud-01 \
    up -d --no-deps --pull never app

echo "===== WAIT FOR STABLE APPLICATION ====="

stable=0

for attempt in $(seq 1 45); do
    if curl --noproxy "*" -fsS --max-time 5 \
        http://127.0.0.1:8080/status.php 2>/dev/null |
        python3 -c 'import json,sys; s=json.load(sys.stdin); assert s.get("installed") is True and s.get("maintenance") is False' 2>/dev/null
    then
        stable=$((stable + 1))
        echo "Backend healthy: $stable/5"
    else
        stable=0
        echo "Backend unavailable; retrying"
    fi

    if [[ "$stable" -ge 5 ]]; then
        break
    fi

    sleep 2
done

test "$stable" -ge 5

echo "===== VERIFY LOOPBACK LISTENER ====="
docker port cloud-01-app-1 80/tcp |
    grep -Fx "127.0.0.1:8080"

echo "===== VERIFY BACKEND AS NGINX USER ====="
runuser -u www-data -- curl --noproxy "*" -fsS     --connect-timeout 3 --max-time 10     http://127.0.0.1:8080/status.php >/dev/null

echo "PASS: Nginx account can reach loopback backend"

echo "===== RELOAD NGINX ====="
nginx -t
systemctl reload nginx

echo "===== HTTPS VERIFICATION ====="

https_ok=0

for attempt in $(seq 1 12); do
    status_code=$(curl --noproxy "*" -sS -o /dev/null \
        --max-time 10 \
        --resolve "$fqdn:443:192.168.2.53" \
        -w "%{http_code}" "https://$fqdn/status.php" \
        2>/dev/null) || status_code=000

    login_code=$(curl --noproxy "*" -sS -o /dev/null \
        --max-time 10 \
        --resolve "$fqdn:443:192.168.2.53" \
        -w "%{http_code}" "https://$fqdn/login" \
        2>/dev/null) || login_code=000

    echo "HTTPS attempt $attempt: status=$status_code login=$login_code"

    if [[ "$status_code" == 200 && "$login_code" == 200 ]]; then
        https_ok=1
        break
    fi

    sleep 3
done

test "$https_ok" = 1

docker port cloud-01-app-1 80/tcp |
    grep -Fx "127.0.0.1:8080"

echo "===== LOCAL ISOLATION CHECK ====="

python3 - <<'PY'
import socket

with socket.socket() as sock:
    sock.settimeout(3)
    result = sock.connect_ex(("192.168.2.53", 8080))

if result == 0:
    raise SystemExit("FAIL: LAN HTTP port remains reachable")

print("PASS: LAN address does not accept HTTP connections")
PY

armed=0
trap - ERR INT TERM

echo "===== CUTOVER SUCCESSFUL ====="
echo "HTTPS_LOGIN=200"
echo "HTTP_BACKEND=127.0.0.1:8080"
