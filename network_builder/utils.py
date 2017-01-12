# encoding: utf-8


'''
Created on 8/12/2016

@author: luisza
'''
from __future__ import unicode_literals

import random

from network_builder.models import Host, Router, Firewall, Link, DHCP,\
    BridgeLink

MAKE_BRIDGE = ['router', 'nat', 'firewall', 'vpn']
DJOBJS = {
    'router': Router,
    'host': Host,
    'firewall': Firewall,
    'dhcp': DHCP,
    'edge': Link,
    'internaledge': BridgeLink
}


RYUAPPS = {
    'router': ['ryu.app.rest_router', 'ryu.controller.ofp_handler', "sdnctlapps.dhcp", 'sdnctlapps.dpinfo'],
    'firewall': ['ryu.app.rest_firewall', 'ryu.controller.ofp_handler', 'sdnctlapps.dpinfo']

}


def get_natural_name(model):
    return model._meta.app_label + "." + model._meta.model_name


def get_apps(nodes):
    app_list = []
    for node in nodes:
        if node['type'] in RYUAPPS:
            app_list += RYUAPPS[node['type']]
    return app_list


def get_random_mac():
    return "00:00:00:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )
