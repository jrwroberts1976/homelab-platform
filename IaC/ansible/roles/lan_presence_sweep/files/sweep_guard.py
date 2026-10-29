"""Accept only successfully completed LAN discovery sweeps."""

import xml.etree.ElementTree as ET

from sweep_parser import parse_sweep


def validated_observations(xml, expected_total):
    root = ET.fromstring(xml)
    finished = root.find("./runstats/finished")
    hosts = root.find("./runstats/hosts")

    if finished is None or finished.get("exit") != "success":
        raise ValueError("Nmap sweep did not complete successfully")

    if hosts is None:
        raise ValueError("Missing Nmap completion statistics")

    try:
        total = int(hosts.attrib["total"])
        up = int(hosts.attrib["up"])
    except (KeyError, ValueError) as exc:
        raise ValueError("Invalid sweep statistics") from exc

    if total != expected_total or up < 1:
        raise ValueError("Incomplete or invalid subnet sweep")

    observed = parse_sweep(xml)
    if len(observed) > up:
        raise ValueError("Inconsistent Nmap host counts")

    return observed


def check_population_drop(previous, observed):
    """Reject a sudden loss of over 60% of established devices."""
    devices = previous.get("devices", {})
    previously_visible = {
        mac for mac, record in devices.items()
        if record.get("observed") is True
    }

    # Small inventories fluctuate too much for this safeguard.
    if len(previously_visible) < 10:
        return

    missing = previously_visible - observed.keys()
    loss_fraction = len(missing) / len(previously_visible)

    if loss_fraction > 0.60:
        raise ValueError(
            "Suspicious sweep: more than 60% of previously "
            "visible devices are missing"
        )
