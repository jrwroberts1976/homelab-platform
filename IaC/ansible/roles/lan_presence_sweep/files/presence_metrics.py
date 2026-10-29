"""Prometheus metrics for MAC-keyed LAN presence."""

import ipaddress
import json

from presence_state import MAC


def render_metrics(state):
    if state.get("schema_version") != 1:
        raise ValueError("Unsupported presence-state schema")

    devices = state["devices"]
    sweep = state["last_successful_sweep"]

    if sweep is None:
        raise ValueError("No successful sweep recorded")

    lines = [
        "# HELP homelab_lan_presence_info Device identity and last known IP.",
        "# TYPE homelab_lan_presence_info gauge",
        "# HELP homelab_lan_presence_host_info Verified host identity.",
        "# TYPE homelab_lan_presence_host_info gauge",
        "# HELP homelab_lan_presence_observed Device appeared in the latest successful sweep.",
        "# TYPE homelab_lan_presence_observed gauge",
        "# HELP homelab_lan_presence_last_seen_seconds Last successful device observation.",
        "# TYPE homelab_lan_presence_last_seen_seconds gauge",
        "# HELP homelab_lan_presence_last_sweep_seconds Last successful LAN sweep.",
        "# TYPE homelab_lan_presence_last_sweep_seconds gauge",
        f"homelab_lan_presence_last_sweep_seconds {sweep}",
    ]

    for mac, record in sorted(devices.items()):
        if not MAC.fullmatch(mac):
            raise ValueError("Invalid inventory MAC")

        ip = str(ipaddress.IPv4Address(record["last_ip"]))
        identity = (
            f"mac={json.dumps(mac)},ip={json.dumps(ip)}"
        )
        observed = 1 if record["observed"] is True else 0


        name = record.get("target_name")
        if name is not None:
            if not isinstance(name, str) or not name.strip() or len(name) > 128:
                raise ValueError("Invalid saved hostname")
            labels = f'mac={json.dumps(mac)},target_name={json.dumps(name)}'
            lines.append(f"homelab_lan_presence_host_info{{{labels}}} 1")

        lines.extend([
            f"homelab_lan_presence_info{{{identity}}} 1",
            f'homelab_lan_presence_observed{{mac={json.dumps(mac)}}} {observed}',
            f'homelab_lan_presence_last_seen_seconds{{mac={json.dumps(mac)}}} '
            f'{record["last_seen"]}',
        ])

    return "\n".join(lines) + "\n"
