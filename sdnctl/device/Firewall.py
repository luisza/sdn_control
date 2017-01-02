# encoding: utf-8


'''
Created on 2/1/2017

@author: luisza
'''
from __future__ import unicode_literals

import json
import requests


class Firewall:

    def __init__(self, instance):
        self.instance = instance
        self.controller = instance.bridge.controller
        self.url = "http://%s:%d/%%s/%s" % (
            self.controller.wsapi_host,
            self.controller.wsapi_port,
            self.instance.switch_id
        )

    def setup(self):
        self.start()
        self.set_rules()

    def start(self):
        url = self.url % "firewall/module/enable"
        response = requests.put(url)
        print (response.text)

    def set_rules(self):
        url = self.url % "firewall/rules"
        fields = ['priority', 'dl_src', 'dl_dst', 'dl_type', 'nw_src',
                  'nw_dst', 'nw_proto', 'tp_src', 'tp_dst', 'actions']
        for rule in self.instance.firewallrule_set.all():
            data = {}
            for field in fields:
                value = getattr(rule, field)
                if value:
                    data[field] = value

            response = requests.post(url, data=json.dumps(data))

            print(url, data)
            print(response.text)
