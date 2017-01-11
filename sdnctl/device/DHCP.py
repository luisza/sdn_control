# encoding: utf-8


'''
Created on 11/1/2017

@author: luisza
'''
from __future__ import unicode_literals

from django.db.models.query_utils import Q
import json

from network_builder.models import Link
from network_builder.utils import get_natural_name
import requests


class DHCP:

    def __init__(self, instance, bridge):
        self.instance = instance
        self.controller = instance.bridge.controller
        self.bridge = bridge

    def setup(self):
        self.create_dhcp_server()
        self.add_static_host()

    def get_primary_nic(self):
        naturalname = get_natural_name(self.instance)
        links = Link.objects.filter(
            Q(to_obj=self.instance.pk,
              to_naturalname=naturalname
              ) | Q(
                from_obj=self.instance.pk,
                from_naturalname=naturalname
            ),
            bridge=self.bridge
        )
        # FIXME: bridge in link
        address = netmask = mac = None
        dhcp = False

        priNIC = links.filter(is_dhcp=False).first()
        if not priNIC:
            priNIC = links.first()
            dhcp = True
        if priNIC:
            address = priNIC.address

        if not dhcp:
            netmask = priNIC.netmask
            mac = priNIC.mac
            #broadcast = priNIC.broadcast

        return address, netmask, mac

    def create_dhcp_server(self):

        url = "http://%s:%d/dhcp/add/%s" % (
            self.controller.wsapi_host,
            self.controller.wsapi_port,
            self.instance.switch_id
        )
        ip, netmask, addr = self.get_primary_nic()
        if ip:
            params = {
                'ipaddress': ip,
                'netmask': netmask,
                'address': addr,
                'dns': self.instance.default_dns or '8.8.8.8',
                'startip': self.instance.start_ip,
                'endip': self.instance.end_ip
            }
            print(url, json.dumps(params))
            response = requests.put(url, data=json.dumps(params))
            print(response.text)

    def add_static_host(self):
        url = "http://%s:%d/dhcp/host/%s" % (
            self.controller.wsapi_host,
            self.controller.wsapi_port,
            self.instance.switch_id
        )

        for staticaddr in self.instance.dhcp_static_ip_set.all():
            params = {'address': staticaddr.mac,
                      'hostname': staticaddr.hostname,
                      'dns': staticaddr.default_dns or '8.8.8.8',
                      'ipaddress': staticaddr.address
                      }
            print(url, json.dumps(params))
            response = requests.put(url, data=json.dumps(params))
            print(response.text)
