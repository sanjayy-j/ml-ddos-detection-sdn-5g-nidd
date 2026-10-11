"""Create an isolated four-host SDN testbed and export switch-side sFlow.

No link to the host's physical network is created. PCAP replay injects only
through a named Mininet host interface. Capture labels must be supplied to
the separate M3 runner and are never inferred from an attack filename.
"""
import argparse
import json
import subprocess
import time
from pathlib import Path

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController


def ovs(*args):
    return subprocess.check_output(["ovs-vsctl", *map(str, args)], text=True).strip()


def set_sampling(rate, target):
    if rate < 1:
        raise ValueError("Sampling N must be positive")
    ovs("--", "--id=@m3sf", "create", "sflow", "agent=lo",
        f'targets=["{target}"]', f"sampling={rate}", "polling=1", "header=256",
        "--", "set", "bridge", "m3s1", "sflow=@m3sf")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sampling", type=int, default=1)
    parser.add_argument("--collector", default="127.0.0.1:6343")
    parser.add_argument("--controller-port", type=int, default=6653)
    parser.add_argument("--datapath", choices=["user", "kernel"], default="user")
    parser.add_argument("--duration", type=float, default=0, help="0 opens Mininet CLI")
    parser.add_argument("--pcap", type=Path, help="Prepared Ethernet PCAP with documented address mapping")
    parser.add_argument("--pps", type=float, default=1000)
    parser.add_argument("--probe", action="store_true", help="Generate only benign ICMP for telemetry validation")
    parser.add_argument("--evidence", type=Path, default=Path("output/sdn/topology.json"))
    args = parser.parse_args()
    if not 0 < args.pps <= 10000:
        parser.error("Replay rate must be between 0 and 10000 packets/s")
    if args.pcap and not args.pcap.resolve().is_file():
        parser.error("Capture does not exist")
    setLogLevel("info")
    # Only this testbed's named bridge is removed, including after a prior failure.
    ovs("--timeout=5", "--if-exists", "del-br", "m3s1")
    net = Mininet(controller=None, switch=OVSSwitch, autoSetMacs=True, autoStaticArp=True)
    net.addController("m3c0", controller=RemoteController, ip="127.0.0.1", port=args.controller_port)
    switch = net.addSwitch("m3s1", protocols="OpenFlow13", datapath=args.datapath, failMode="secure")
    hosts = [net.addHost(name, ip=f"10.77.0.{index}/24") for index, name in enumerate(
        ["m3a1", "m3a2", "m3benign", "m3victim"], start=1)]
    for host in hosts:
        net.addLink(host, switch)
    try:
        net.start()
        time.sleep(2)
        set_sampling(args.sampling, args.collector)
        loss = net.pingAll(timeout="2")
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence = {"topology": "isolated_m3_four_hosts", "sampling_rate": args.sampling,
                    "collector": args.collector, "ping_loss_percent": loss, "datapath": args.datapath,
                    "flow_table": subprocess.check_output(["ovs-ofctl", "-O", "OpenFlow13", "dump-flows", "m3s1"], text=True),
                    "pcap": str(args.pcap.resolve()) if args.pcap else None,
                    "replay_pps": args.pps if args.pcap else None,
                    "started_epoch": time.time(), "quality_ground_truth": "supplied separately; not inferred"}
        args.evidence.write_text(json.dumps(evidence, indent=2) + "\n")
        if loss:
            raise RuntimeError("Controller/topology connectivity failed; inspect controller log")
        if args.probe:
            hosts[2].cmd(f"ping -q -i 0.01 -c {max(100, int(args.duration * 80))} 10.77.0.4 >/dev/null 2>&1 &")
        if args.pcap:
            # pcap paths are passed as argv, never interpolated into a shell command.
            replay = hosts[0].popen(["tcpreplay", "--intf1=m3a1-eth0", f"--pps={args.pps}",
                                     "--loop=1", str(args.pcap.resolve())])
        else:
            replay = None
        if args.duration:
            time.sleep(args.duration)
        else:
            CLI(net)
        if replay and replay.poll() is None:
            replay.terminate()
            replay.wait(timeout=5)
    finally:
        net.stop()


if __name__ == "__main__":
    main()
