"""Read-only checks for Linux/WSL SDN prerequisites."""

import json
import os
import shutil
import subprocess
import sys


def main():
    checks = {
        "linux": sys.platform == "linux",
        "root": hasattr(os, "geteuid") and os.geteuid() == 0,
        "tun_device": os.path.exists("/dev/net/tun"),
    }
    for executable in ["ovs-vsctl", "ovs-vswitchd", "ip", "ping", "tcpreplay", "tcpdump"]:
        checks[executable] = bool(shutil.which(executable))
    for package in ["mininet", "os_ken"]:
        try:
            __import__(package)
            checks[package] = True
        except ImportError:
            checks[package] = False
    if checks["ovs-vsctl"]:
        result = subprocess.run(
            ["ovs-vsctl", "--timeout=3", "show"], check=False, capture_output=True, text=True
        )
        checks["ovs_database"] = result.returncode == 0
    print(json.dumps(checks, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
