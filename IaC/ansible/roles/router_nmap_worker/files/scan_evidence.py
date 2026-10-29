"""Validate and extract Nmap OS and service evidence."""

import xml.etree.ElementTree as ET


def validate_scan_xml(xml, expected_ip):
    root = ET.fromstring(xml)

    if root.tag != "nmaprun":
        raise ValueError("Unexpected Nmap XML root")

    finished = root.find("./runstats/finished")

    if finished is None or finished.get("exit") != "success":
        raise ValueError("Nmap scan did not finish successfully")

    matches = []

    for host in root.findall("host"):
        addresses = [
            address.get("addr", "")
            for address in host.findall("address")
            if address.get("addrtype") == "ipv4"
        ]

        if expected_ip in addresses:
            matches.append(host)

    if len(matches) != 1:
        raise ValueError(
            "Expected exactly one host matching " + expected_ip
        )

    host = matches[0]
    status = host.find("status")

    if status is None or status.get("state") != "up":
        raise ValueError("Target host is not marked up")

    return host


def parse_host(xml, expected_ip):
    host = validate_scan_xml(xml, expected_ip)

    os_matches = []

    for match in host.findall("./os/osmatch")[:5]:
        classes = []

        for item in match.findall("osclass")[:5]:
            classes.append({
                "type": item.get("type", ""),
                "vendor": item.get("vendor", ""),
                "os_family": item.get("osfamily", ""),
                "os_generation": item.get("osgen", ""),
                "accuracy": item.get("accuracy", ""),
                "cpe": [
                    element.text
                    for element in item.findall("cpe")
                    if element.text
                ],
            })

        os_matches.append({
            "name": match.get("name", ""),
            "accuracy": match.get("accuracy", ""),
            "classes": classes,
        })

    ports = []

    for port in host.findall("./ports/port"):
        state = port.find("state")

        if state is None:
            continue

        state_name = state.get("state", "")

        if state_name not in (
            "open",
            "open|filtered",
        ):
            continue

        service = port.find("service")

        service_data = {
            "name": "",
            "product": "",
            "version": "",
            "extra_info": "",
            "os_type": "",
            "device_type": "",
            "hostname": "",
            "tunnel": "",
            "cpe": [],
        }

        if service is not None:
            service_data.update({
                "name": service.get("name", ""),
                "product": service.get("product", ""),
                "version": service.get("version", ""),
                "extra_info": service.get(
                    "extrainfo",
                    "",
                ),
                "os_type": service.get(
                    "ostype",
                    "",
                ),
                "device_type": service.get(
                    "devicetype",
                    "",
                ),
                "hostname": service.get(
                    "hostname",
                    "",
                ),
                "tunnel": service.get(
                    "tunnel",
                    "",
                ),
                "cpe": [
                    element.text
                    for element in service.findall("cpe")
                    if element.text
                ],
            })

        scripts = {}

        for script in port.findall("script"):
            output = " ".join(
                script.get("output", "").split()
            )

            # Keep detail in JSON, but bound individual output.
            scripts[script.get("id", "")] = output[:4000]

        ports.append({
            "protocol": port.get("protocol", ""),
            "port": int(
                port.get("portid", "0")
            ),
            "state": state_name,
            "service": service_data,
            "scripts": scripts,
        })

    ports.sort(
        key=lambda item: (
            item["protocol"],
            item["port"],
        )
    )

    return {
        "os_matches": os_matches,
        "ports": ports,
    }
