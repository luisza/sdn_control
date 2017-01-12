# encoding: utf-8


'''
Created on 4/12/2016

@author: luisza
'''
from __future__ import unicode_literals

from sdnctl.models import RyuApp
NAMES = ('ryu.app.wsgi', 'ryu.app.rest_firewall', 'ryu.app.rest_topology', 'ryu.app.rest_qos', 'ryu.app.simple_switch_websocket_13', 'ryu.app.simple_switch_snort', 'ryu.app.simple_switch_stp', 'ryu.app.ws_topology', 'ryu.app.example_switch_13', 'ryu.app.simple_switch_13', 'ryu.app.simple_switch_12', 'ryu.app.simple_switch_14',
         'ryu.app.rest_conf_switch', 'ryu.app.ofctl_rest', 'ryu.app.simple_switch', 'ryu.app.bmpstation', 'ryu.app.simple_switch_lacp', 'ryu.app.simple_switch_igmp', 'ryu.app.cbench', 'ryu.app.conf_switch_key', 'ryu.app.gui_topology', 'ryu.app.rest_router', 'ryu.app.ofctl.api', 'ryu.app.ofctl.event', 'ryu.app.ofctl.service')


for name in NAMES:
    RyuApp.objects.get_or_create(
        name=name,
        app_code=name
    )
