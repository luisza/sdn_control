# Copyright (C) 2013 Nippon Telegraph and Telephone Corporation.
# Copyright (C) 2013 YAMAMOTO Takashi <yamamoto at valinux co jp>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# a simple ICMP Echo Responder

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import addrconv
from ryu.lib.packet import dhcp
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import packet
from ryu.lib.packet import udp
from ryu.ofproto import ofproto_v1_3


class DHCPResponder(app_manager.RyuApp):
    """
    use example
        self.switches = {
            '81474781969487': {
                'ipaddress': '192.168.1.1',
                'netmask': '255.255.255.0',
                'address': '0a:e4:1c:d1:3e:44',
                'dns': '8.8.8.8',
                'hosts': {
                    '00:00:00:d3:fc:57': {
                        'hostname': 'huehuehue',
                        'dns': '8.8.8.8',
                        'ipaddress':  '192.168.1.2',
                    }
                },
                'available_address': [
                    '192.168.1.10',
                    '192.168.1.20'
                ]

            }}
    """

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(DHCPResponder, self).__init__(*args, **kwargs)
        self.acks = {}
        self.switches = {}

    def get_server_info(self, datapath):
        if datapath in self.switches:
            ipaddress = addrconv.ipv4.text_to_bin(
                self.switches[datapath]['ipaddress'])
            netmask = addrconv.ipv4.text_to_bin(
                self.switches[datapath]['netmask'])
            address = self.switches[datapath]['address']
            return ipaddress, netmask, address, self.switches[datapath]['ipaddress']
        return None, None, None, None

    def get_host_info(self, datapath, hostaddress):
        #print(datapath, hostaddress)
        ipaddress = hostname = dns = None
        if datapath in self.switches:
            if hostaddress in self.acks:
                info = self.acks[hostaddress]
                return info['ipaddress'], info['hostname'], info['dns']

            if hostaddress in self.switches[datapath]['hosts']:
                confhost = self.switches[datapath]['hosts'][hostaddress]
                ipaddress = confhost['ipaddress']
                hostname = confhost['hostname']
                dns = addrconv.ipv4.text_to_bin(confhost['dns'])
            if not ipaddress and self.switches[datapath]['available_address']:
                ipaddress = self.switches[datapath]['available_address'].pop()
                num = ipaddress.split('.')[-1]
                hostname = "machine" + num
                dns = addrconv.ipv4.text_to_bin(self.switches[datapath]['dns'])
                self.acks[hostaddress] = {
                    'ipaddress': ipaddress,
                    'hostname': hostname,
                    'dns': dns
                }
        return ipaddress, hostname, dns

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def _switch_features_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        actions = [parser.OFPActionOutput(port=ofproto.OFPP_CONTROLLER,
                                          max_len=ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(type_=ofproto.OFPIT_APPLY_ACTIONS,
                                             actions=actions)]
        mod = parser.OFPFlowMod(datapath=datapath,
                                priority=0,
                                match=parser.OFPMatch(),
                                instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        port = msg.match['in_port']
        pkt = packet.Packet(data=msg.data)
        pkt_dhcp = pkt.get_protocols(dhcp.dhcp)
        if pkt_dhcp:
            self._handle_dhcp(datapath, port, pkt)

    def assemble_ack(self, pkt, datapath):
        req_eth = pkt.get_protocol(ethernet.ethernet)
        req_ipv4 = pkt.get_protocol(ipv4.ipv4)
        req = pkt.get_protocol(dhcp.dhcp)

        ipaddress, netmask, address, dhcpip = self.get_server_info(datapath)
        hostipaddress, hostname, dns = self.get_host_info(datapath,
                                                          req_eth.src)
        if ipaddress:
            req.options.option_list.remove(
                next(opt for opt in req.options.option_list if opt.tag == 53))
            req.options.option_list.insert(
                0, dhcp.option(tag=51, value='8640'))
            req.options.option_list.insert(
                0, dhcp.option(tag=53, value='05'.decode('hex')))

            ack_pkt = packet.Packet()
            ack_pkt.add_protocol(ethernet.ethernet(
                ethertype=req_eth.ethertype, dst=req_eth.src, src=address))
            ack_pkt.add_protocol(
                ipv4.ipv4(dst=req_ipv4.dst, src=dhcpip, proto=req_ipv4.proto))
            ack_pkt.add_protocol(udp.udp(src_port=67, dst_port=68))
            ack_pkt.add_protocol(dhcp.dhcp(op=2, chaddr=req_eth.src,
                                           siaddr=dhcpip,
                                           boot_file=req.boot_file,
                                           yiaddr=hostipaddress,
                                           xid=req.xid,
                                           options=req.options))
            self.logger.info("ASSEMBLED ACK: %s -> %s" %
                             (req_eth.src, hostipaddress))
        return ack_pkt

    def assemble_offer(self, pkt, datapath):
        disc_eth = pkt.get_protocol(ethernet.ethernet)
        disc_ipv4 = pkt.get_protocol(ipv4.ipv4)
        disc = pkt.get_protocol(dhcp.dhcp)
        offer_pkt = None
        ipaddress, netmask, address, dhcpip = self.get_server_info(datapath)
        hostipaddress, hostname, dns = self.get_host_info(
            datapath, disc_eth.src)
        if ipaddress:
            disc.options.option_list.remove(
                next(opt for opt in disc.options.option_list if opt.tag == 55))
            disc.options.option_list.remove(
                next(opt for opt in disc.options.option_list if opt.tag == 53))
            disc.options.option_list.remove(
                next(opt for opt in disc.options.option_list if opt.tag == 12))
            disc.options.option_list.insert(
                0, dhcp.option(tag=1, value=netmask))
            disc.options.option_list.insert(
                0, dhcp.option(tag=3, value=ipaddress))
            disc.options.option_list.insert(
                0, dhcp.option(tag=6, value=dns))
            disc.options.option_list.insert(
                0, dhcp.option(tag=12, value=hostname))
            disc.options.option_list.insert(
                0, dhcp.option(tag=53, value='02'.decode('hex')))
            disc.options.option_list.insert(
                0, dhcp.option(tag=54, value=ipaddress))

            offer_pkt = packet.Packet()
            offer_pkt.add_protocol(ethernet.ethernet(
                ethertype=disc_eth.ethertype, dst=disc_eth.src, src=address))
            offer_pkt.add_protocol(
                ipv4.ipv4(dst=disc_ipv4.dst, src=dhcpip, proto=disc_ipv4.proto))
            offer_pkt.add_protocol(udp.udp(src_port=67, dst_port=68))
            offer_pkt.add_protocol(dhcp.dhcp(op=2, chaddr=disc_eth.src,
                                             siaddr=dhcpip,
                                             boot_file=disc.boot_file,
                                             yiaddr=hostipaddress,
                                             xid=disc.xid,
                                             options=disc.options))
            self.logger.info("ASSEMBLED OFFER: %s --> %s" %
                             (disc_eth.src, hostipaddress))
        return offer_pkt

    def get_state(self, pkt_dhcp):
        dhcp_state = ord(
            [opt for opt in pkt_dhcp.options.option_list if opt.tag == 53][0].value)
        if dhcp_state == 1:
            state = 'DHCPDISCOVER'
        elif dhcp_state == 2:
            state = 'DHCPOFFER'
        elif dhcp_state == 3:
            state = 'DHCPREQUEST'
        elif dhcp_state == 5:
            state = 'DHCPACK'
        return state

    def _handle_dhcp(self, datapath, port, pkt):

        pkt_dhcp = pkt.get_protocols(dhcp.dhcp)[0]
        dhcp_state = self.get_state(pkt_dhcp)
        self.logger.info("NEW DHCP %s PACKET RECEIVED: %s" %
                         (dhcp_state, pkt_dhcp.chaddr))
        if dhcp_state == 'DHCPDISCOVER':
            discover = self.assemble_offer(pkt, str(datapath.id))
            if discover:
                self._send_packet(datapath, port, discover)
        elif dhcp_state == 'DHCPREQUEST':
            ack = self.assemble_ack(pkt, str(datapath.id))
            if ack:
                self._send_packet(datapath, port, ack)

    def _send_packet(self, datapath, port, pkt):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt.serialize()
        #self.logger.info("packet-out %s" % (pkt,))
        data = pkt.data
        actions = [parser.OFPActionOutput(port=port)]
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER,
                                  actions=actions,
                                  data=data)
        datapath.send_msg(out)
