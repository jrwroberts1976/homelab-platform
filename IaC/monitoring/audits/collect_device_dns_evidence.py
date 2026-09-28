#!/usr/bin/env python3
"""Collect minimised DNS evidence for one LAN device from both Pi-hole servers.

Safety:
- one target IP only
- read-only sqlite3 queries over SSH
- seven-day default lookback
- aggregates only: query_count + top_domains
- no raw DNS log persistence
"""

import argparse
import ipaddress
import json
import shlex
import subprocess
import sys
import time

SERVERS = {
    "dns-01": "192.168.2.51",
    "dns-02": "192.168.2.50",
}
DEFAULT_DB = "/etc/pihole/pihole-FTL.db"


def validate_target(value):
    ip = ipaddress.ip_address(value)
    if ip.version != 4 or ip not in ipaddress.ip_network("192.168.2.0/24"):
        raise argparse.ArgumentTypeError("target must be an IPv4 address in 192.168.2.0/24")
    return str(ip)


def run_ssh(host, user, key, remote):
    cmd = [
        "ssh",
        "-T",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=10",
    ]
    if key:
        cmd += ["-i", key]
    cmd += [f"{user}@{host}", remote]

    result = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=45,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"SSH/query failed for {host}: {result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout


def build_remote_query(target_ip, since_epoch, limit, db_path):
    # Pi-hole v6 FTL stores normalised client/domain IDs in query_storage.
    # The query is SELECT-only and sqlite3 is opened read-only.
    sql = f"""
PRAGMA query_only=ON;
.mode tabs
WITH per_domain AS (
  SELECT d.domain AS domain, COUNT(*) AS c
  FROM query_storage q
  JOIN client_by_id c ON c.id = q.client
  JOIN domain_by_id d ON d.id = q.domain
  WHERE c.ip = {json.dumps(target_ip)}
    AND q.timestamp >= {int(since_epoch)}
  GROUP BY d.domain
),
ranked AS (
  SELECT domain, c
  FROM per_domain
  ORDER BY c DESC, domain ASC
  LIMIT {int(limit)}
)
SELECT 'COUNT', COALESCE((
  SELECT COUNT(*)
  FROM query_storage q
  JOIN client_by_id c ON c.id = q.client
  WHERE c.ip = {json.dumps(target_ip)}
    AND q.timestamp >= {int(since_epoch)}
), 0);
SELECT 'DOMAIN', domain, c FROM ranked;
"""
    remote = (
        "sqlite3 -readonly "
        + shlex.quote(db_path)
        + " "
        + shlex.quote(sql)
    )
    return remote


def parse_rows(text):
    total = 0
    domains = []
    for raw in text.splitlines():
        parts = raw.split("\t")
        if not parts:
            continue
        if parts[0] == "COUNT" and len(parts) >= 2:
            total = int(parts[1] or 0)
        elif parts[0] == "DOMAIN" and len(parts) >= 3:
            domains.append({
                "domain": parts[1],
                "count": int(parts[2] or 0),
            })
    return total, domains


def collect(target_ip, days, limit, user, key, db_path):
    now = int(time.time())
    since = now - (int(days) * 86400)
    records = []

    for name, host in SERVERS.items():
        remote = build_remote_query(target_ip, since, limit, db_path)
        output = run_ssh(host, user, key, remote)
        total, domains = parse_rows(output)
        records.append({
            "ip": target_ip,
            "server": name,
            "query_count": total,
            "top_domains": [item["domain"] for item in domains],
            "top_domain_counts": domains,
            "window_days": int(days),
            "collected_at": now,
        })

    return records


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("ip", type=validate_target)
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--top", type=int, default=5)
    p.add_argument("--ssh-user", default="root")
    p.add_argument("--ssh-key")
    p.add_argument("--db", default=DEFAULT_DB)
    p.add_argument("--output", help="Optional JSON output file; stdout is always emitted")
    args = p.parse_args()

    if not 1 <= args.days <= 30:
        p.error("--days must be between 1 and 30")
    if not 1 <= args.top <= 10:
        p.error("--top must be between 1 and 10")

    try:
        records = collect(
            args.ip, args.days, args.top,
            args.ssh_user, args.ssh_key, args.db,
        )
    except Exception as exc:
        print(f"dns_evidence_collection_failed: {exc}", file=sys.stderr)
        return 1

    payload = json.dumps(records, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(payload)
    sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
