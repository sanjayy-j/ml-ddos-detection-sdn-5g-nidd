"""Learning-switch controller for the isolated M3 topology (OpenFlow 1.3).

Run: /opt/m3-sdn/bin/osken-manager --ofp-tcp-listen-port 6653 sdn/controller.py
The model and labels never enter the controller's forwarding rules.
"""

from typing import ClassVar

from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from os_ken.lib.packet import ether_types, ethernet, packet
from os_ken.ofproto import ofproto_v1_3


class M3LearningSwitch(app_manager.OSKenApp):
    OFP_VERSIONS: ClassVar[list[int]] = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features(self, event):
        datapath = event.msg.datapath
        parser, proto = datapath.ofproto_parser, datapath.ofproto
        actions = [parser.OFPActionOutput(proto.OFPP_CONTROLLER, proto.OFPCML_NO_BUFFER)]
        self.install(datapath, 0, parser.OFPMatch(), actions)

    def install(self, datapath, priority, match, actions):
        parser = datapath.ofproto_parser
        instruction = parser.OFPInstructionActions(datapath.ofproto.OFPIT_APPLY_ACTIONS, actions)
        datapath.send_msg(
            parser.OFPFlowMod(
                datapath=datapath,
                priority=priority,
                idle_timeout=30 if priority else 0,
                match=match,
                instructions=[instruction],
            )
        )

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in(self, event):
        message = event.msg
        datapath = message.datapath
        parser, proto = datapath.ofproto_parser, datapath.ofproto
        incoming = message.match["in_port"]
        header = packet.Packet(message.data).get_protocol(ethernet.ethernet)
        if header is None or header.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        addresses = self.mac_to_port.setdefault(datapath.id, {})
        addresses[header.src] = incoming
        outgoing = addresses.get(header.dst, proto.OFPP_FLOOD)
        actions = [parser.OFPActionOutput(outgoing)]
        if outgoing != proto.OFPP_FLOOD:
            self.install(
                datapath,
                1,
                parser.OFPMatch(in_port=incoming, eth_src=header.src, eth_dst=header.dst),
                actions,
            )
        datapath.send_msg(
            parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=message.buffer_id,
                in_port=incoming,
                actions=actions,
                data=message.data if message.buffer_id == proto.OFP_NO_BUFFER else None,
            )
        )
