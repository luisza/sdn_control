# encoding: utf-8


'''
Created on 1/1/2017

@author: luisza
'''
from __future__ import unicode_literals

import json

import requests


class Router:

    def __init__(self, instance):
        self.instance = instance
        self.controller = instance.bridge.controller
        self.url = "http://%s:%d/router/%s" % (
            self.controller.wsapi_host,
            self.controller.wsapi_port,
            self.instance.switch_id
        )

    def setup(self):
        self.set_ip_address()
        self.set_networks()
        self.get_info()

    def get_info(self):
        response = requests.get(self.url)
        print(response.content)

    def set_ip_address(self):
        for addr in self.instance.routeraddress_set.all():
            data = {
                'address': addr.address
            }
            print(self.url, json.dumps(data))
            response = requests.post(self.url, data=json.dumps(data))
            print(response.text)

        if self.instance.default_gateway:
            print(self.url, json.dumps({
                'gateway': self.instance.default_gateway
            }))
            response = requests.post(self.url, data=json.dumps({
                'gateway': self.instance.default_gateway
            }))
            print(response.text)

    def set_networks(self):

        for net in self.instance.network_set.all():
            data = {"destination": net.network,
                    "gateway": net.gateway}
            response = requests.post(self.url, data=json.dumps(data))
            print(response.text)
