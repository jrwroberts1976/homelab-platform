"""Match monitored hostnames to MACs verified by the LAN sweep."""

import ipaddress

from presence_state import MAC


def verified_hostnames(observed, series):
    matches = {}
    conflicts = set()

    for item in series:
        labels = item.get("metric", {})
        mac = labels.get("address", "").lower()
        name = labels.get("target_name", "")
        instance = labels.get("instance", "")

        if not MAC.fullmatch(mac) or not name or len(name) > 128:
            continue

        try:
            ip = str(ipaddress.IPv4Address(
                instance.rsplit(":", 1)[0]
            ))
        except ValueError:
            continue

        # Both the network address and MAC must match this sweep.
        if observed.get(mac) != ip:
            continue

        if mac in matches and matches[mac] != name:
            conflicts.add(mac)
        else:
            matches[mac] = name

    for mac in conflicts:
        matches.pop(mac, None)

    return matches


def fetch_exporter_interfaces(
    url="http://127.0.0.1:9090/api/v1/query",
    timeout=5,
):
    """Retrieve current Node Exporter interface evidence."""
    import json
    import urllib.parse
    import urllib.request

    parameters = urllib.parse.urlencode({
        "query": 'node_network_info{job="node-exporter"}'
    })

    with urllib.request.urlopen(
        url + "?" + parameters,
        timeout=timeout,
    ) as response:
        result = json.load(response)

    if (
        result.get("status") != "success"
        or result.get("data", {}).get("resultType") != "vector"
        or not isinstance(result["data"].get("result"), list)
    ):
        raise ValueError("Invalid Prometheus interface response")

    return result["data"]["result"]


def attach_verified_hostnames(state, verified, timestamp):
    """Preserve verified host identities across later missed sweeps."""
    import copy

    if state.get("schema_version") != 1:
        raise ValueError("Unsupported presence-state schema")

    updated = copy.deepcopy(state)

    for mac, name in verified.items():
        if (
            not MAC.fullmatch(mac)
            or not isinstance(name, str)
            or not name.strip()
            or len(name) > 128
        ):
            raise ValueError("Invalid verified host identity")

        record = updated["devices"].get(mac)

        # Only associate a hostname with a MAC actually
        # observed in the current successful sweep.
        if record is None or record.get("observed") is not True:
            continue

        record["target_name"] = name
        record["hostname_verified_at"] = timestamp

    return updated
