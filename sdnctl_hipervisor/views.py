# encoding: utf-8


'''
Created on 9/12/2016

@author: luisza
'''
from __future__ import unicode_literals

from django.http.response import HttpResponse

from network_builder.models import NetworkBridge
from sdnctl.device.Bridge import Bridge
from sdnctl.shell.bashclient import BashClient


def create_bridges(request, net, pk):
    bridges = NetworkBridge.objects.filter(
        network_instance__pk=net, pk=pk)

    shell = BashClient()
    cbridges = []
    for bridge in bridges:
        bg = Bridge(bridge, shell)
        bg.create_bridge()
        bg.create_internal_ports()
        cbridges.append(bg)

    for bridge in cbridges:
        bridge.create_peer_internal_ports()
        bridge.create_dhcp()
        bridge.create_host()

    return HttpResponse("OK")
