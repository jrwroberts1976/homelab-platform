#!/usr/bin/env python3
"""Opt-in sensor-01 ONLY: real isolated kernel test through Python journal lifecycle.

No PPP hooks, router interfaces, systemd or SIGKILL. Test namespace is deleted in
finally. The synthetic watchdog callback is NOT an independent rollback watchdog.
"""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import fcntl

def load(filename, alias):
    spec=importlib.util.spec_from_file_location(alias,Path(__file__).with_name(filename))
    module=importlib.util.module_from_spec(spec)
    sys.modules[alias]=module
    spec.loader.exec_module(module)
    return module

def cmd(*argv, check=True):
    return subprocess.run(argv, text=True, capture_output=True, timeout=8, check=check)

def main():
    if len(sys.argv)!=2 or sys.argv[1]!="--approved" or os.geteuid()!=0:
        raise RuntimeError("explicit approval and root required")
    if cmd("hostname","-s").stdout.strip()!="sensor-01":
        raise RuntimeError("sensor-01 only")
    life=load("router-qos-download-integrated-offline.py","qos_live_disposable_lifecycle")
    ns=life.NAMESPACE
    source=life.SOURCE
    ifb=life.IFB
    if ns in [line.split()[0] for line in cmd("ip","netns","list").stdout.splitlines()]:
        raise RuntimeError("test namespace already exists; refuse foreign resources")
    fd=os.open("/run/lock/qos-p5-python-e2e.lock",os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    try:
        fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if ns in [line.split()[0] for line in cmd("ip","netns","list").stdout.splitlines()]:
            raise RuntimeError("test namespace created by another process")
        created=False
        try:
            cmd("ip","netns","add",ns)
            created=True
            cmd("ip","-n",ns,"link","add",source,"type","dummy")
            cmd("ip","-n",ns,"link","set",source,"up")
            ns_inode=os.stat("/run/netns/"+ns).st_ino
            host_inode=os.stat("/proc/1/ns/net").st_ino
            if ns_inode==host_inode:
                raise RuntimeError("namespace not isolated")
            session={"generation":"qos-p5-test","ifindex":int(cmd("ip","-n",ns,"-o","link","show","dev",source).stdout.split(":")[0])}
            def namespace_ok():
                return (os.stat("/run/netns/"+ns).st_ino==ns_inode and
                        os.stat("/proc/1/ns/net").st_ino==host_inode)
            def inspect(target):
                if not namespace_ok():
                    return False
                q=cmd("ip","netns","exec",ns,"tc","qdisc","show","dev",ifb,check=False)
                f=cmd("ip","netns","exec",ns,"tc","filter","show","dev",source,"ingress",check=False)
                s=cmd("ip","netns","exec",ns,"tc","qdisc","show","dev",source,check=False)
                exists=cmd("ip","-n",ns,"link","show","dev",ifb,check=False).returncode==0
                if target is None:
                    return not exists and not f.stdout.strip() and "clsact" not in s.stdout and "ingress" not in s.stdout
                return (target==session and exists and q.returncode==0 and
                        "cake" in q.stdout and "43Mbit" in q.stdout and
                        f.returncode==0 and "mirred" in f.stdout and "clsact" in s.stdout)
            def runner(argv):
                if not namespace_ok() or argv[:4]!=["ip","netns","exec",ns] or argv not in life.actions(True)+life.actions(False):
                    return False
                return cmd(*argv,check=False).returncode==0
            with tempfile.TemporaryDirectory(prefix="qos-p5-journal-") as directory:
                flow=life.OfflineLifecycle(directory,runner=runner,observe=inspect,watchdog=namespace_ok)
                if flow.transition(None,session)!="COMMITTED" or flow.inspect()["owned"]!=session:
                    raise RuntimeError("install verification failed")
                print("PASS: integrated Python 43 Mbps IFB/CAKE install committed",flush=True)
                if flow.transition(session,None)!="COMMITTED" or flow.inspect()["owned"] is not None:
                    raise RuntimeError("teardown verification failed")
                print("PASS: integrated Python teardown committed",flush=True)
        finally:
            if created:
                cmd("ip","netns","del",ns)
                print("PASS: test namespace removed",flush=True)
    finally:
        os.close(fd)

if __name__=="__main__":
    main()
