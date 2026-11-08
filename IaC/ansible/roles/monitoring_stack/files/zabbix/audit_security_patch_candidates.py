#!/usr/bin/env python3
"""Read-only evidence audit before claiming a security patch count."""
import json
import re
import shutil
import subprocess
from pathlib import Path

def run(argv):
    p = subprocess.run(argv, capture_output=True, text=True, timeout=25,
                       env={"LC_ALL": "C", "PATH": "/usr/sbin:/usr/bin:/sbin:/bin"})
    return {"rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr}

def main():
    q = run(["apt", "list", "--upgradable"])
    if q["rc"] != 0:
        raise SystemExit("cached APT candidate query failed")
    candidates = []
    for line in q["stdout"].splitlines():
        if not line or line.startswith("Listing"):
            continue
        m = re.match(r"^([^/]+)/\S+\s+(\S+)\s", line)
        if not m:
            raise SystemExit("unexpected apt list row; refusing classification")
        name, version = m.groups()
        p = run(["apt-cache", "policy", name])
        if p["rc"] != 0:
            raise SystemExit("apt-cache policy failure for " + name)
        selected = []
        active = False
        for l in p["stdout"].splitlines():
            v = re.match(r"^\s*(?:\*\*\*\s+)?(\S+)\s+\d+\s*$", l)
            if v:
                active = v.group(1) == version
            elif active and ("release " in l or "http:" in l or "https:" in l):
                selected.append(l.strip())
        candidates.append({
            "package": name,
            "candidate_version": version,
            "candidate_repository_evidence": selected[:8],
        })
    sources = run(["apt-cache", "policy"])
    origin_lines = [l.strip() for l in sources["stdout"].splitlines()
                    if "release " in l or "security" in l.lower()]
    tools = {name: bool(shutil.which(name))
             for name in ("debsecan", "python3", "apt-cache", "dpkg-query")}
    paths = [str(p) for directory in (Path("/etc/apt/sources.list.d"),)
             if directory.is_dir() for p in directory.iterdir()
             if p.suffix in (".sources", ".list")]
    print(json.dumps({
        "mode": "READ_ONLY_EVIDENCE",
        "package_count": len(candidates),
        "available_tools": tools,
        "apt_source_paths": sorted(paths),
        "repository_policy_security_lines": origin_lines[:50],
        "candidates": candidates,
        "security_patch_count": None,
        "reason": ("Repository labels alone do not classify all security fixes, "
                   "especially vendor and ordinary stable update repositories."),
    }, indent=2))

if __name__ == "__main__":
    main()
