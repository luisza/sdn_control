# encoding: utf-8


'''
Created on 9/12/2016

@author: luisza
'''
from __future__ import unicode_literals
from network_builder.models import BridgeLink, Host
from sdnctl.device.Host import Host as Dhost


class Bridge(object):

    def __init__(self, instance, bash):
        self.instance = instance
        self._bash = bash

    def delete_bridge(self):
        name = "n%d_%d" % (self.instance.network_instance.pk, self.instance.pk)
        self._bash.execute('sudo ovs-vsctl del-br %s' % (name,))

    def create_bridge(self):
        bridge = self.instance
        name = "n%d_%d" % (bridge.network_instance.pk, bridge.pk)

        if bridge:
            self._bash.execute(
                'sudo ovs-vsctl --may-exist add-br %s' % (name,))
            self._bash.execute("sudo ovs-vsctl set-controller %s tcp:%s" % (
                name,
                bridge.controller.get_controller_ip()
            ))
            self._bash.execute("sudo ip link set %s up multicast on" % (name,))

    def create_internal_ports(self):
        bridge = self.instance
        net = bridge.network_instance.pk
        name = "n%d_%d" % (net, bridge.pk)

        if bridge:
            blinks = BridgeLink.objects.filter(
                network_instance__pk=net, base=bridge)
            for br in blinks:
                for peer in br.related_bridges.all():
                    port_name = "n%d_%s_to_%s" % (net, bridge.pk, peer.pk)
                    peer_name = "n%d_%s_to_%s" % (net, peer.pk, bridge.pk)

                    cmd = "sudo ovs-vsctl --may-exist add-port %s %s " % (
                        name, port_name)
                    cmd += "-- set interface %s type=patch options:peer=%s" % (
                        port_name, peer_name)
                    self._bash.execute(cmd)

    def create_peer_internal_ports(self):
        bridge = self.instance
        net = bridge.network_instance.pk
        name = "n%d_%d" % (net, bridge.pk)
        if bridge:
            peers = BridgeLink.objects.filter(
                related_bridges=bridge).distinct()

            for peer in peers:
                port_name = "n%d_%s_to_%s" % (net, bridge.pk, peer.base.pk)
                peer_name = "n%d_%s_to_%s" % (net, peer.base.pk, bridge.pk)
                cmd = "sudo ovs-vsctl --may-exist add-port %s %s " % (
                    name, port_name)
                cmd += "-- set interface %s type=patch options:peer=%s" % (
                    port_name, peer_name)
                self._bash.execute(cmd)

    def create_host(self):
        hosts = Host.objects.filter(bridge=self.instance)
        for h in hosts:
            p = Dhost(h, self._bash)
            p.create_host()
