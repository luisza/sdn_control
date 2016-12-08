# encoding: utf-8


'''
Created on 8/12/2016

@author: luisza
'''
from __future__ import unicode_literals
import pprint
from network_builder.models import Router, Firewall, Link
from sdnctl.models import Host, DHCP_Server


MAKE_BRIDGE = ['router', 'nat', 'firewall', 'vpn']
DJOBJS = {
    'router': Router,
    'host': Host,
    'firewall': Firewall,
    'dhcp': DHCP_Server,
    'egdes': Link
}


RYUAPPS = {
    'router': ['ryu.app.rest_router'],
    'firewall': ['ryu.app.rest_firewall']
}


def get_django_object(node):
    if 'djvalue' in node:
        return DJOBJS[node['type']].objects.get(pk=node['djvalue'])


def build_network(data, name):
    bridges = {}
    for i, node in enumerate(data['nodes']):
        if 'djvalue' in node:
            data['nodes'][i]['obj'] = get_django_object(node)
            node = data['nodes'][i]
        if node['type'] in MAKE_BRIDGE:
            bridges[name + '_' + node['type'] +
                    '_' + str(node['id'])] = {'ports': [],
                                              'objs': [node]}

    for edge in data['edges']:
        edge['type'] = 'edges'
        if 'djvalue' in edge:
            data['edges'][i]['obj'] = get_django_object(edge)
            edge = data['edges'][i]
        to = list(filter(lambda x: x['id'] == edge['to'], data['nodes']))
        _from = list(filter(lambda x: x['id'] == edge['from'], data['nodes']))
        if len(to) == 0 or len(_from) == 0:
            continue
        to, _from = to[0], _from[0]

        if to['type'] in MAKE_BRIDGE and _from['type'] in MAKE_BRIDGE:
            from_br = name + '_' + _from['type'] + '_' + str(_from['id'])
            to_br = name + '_' + to['type'] + '_' + str(to['id'])
            bridges[from_br]['ports'].append(
                {
                    'from': from_br,
                    'to': to_br,
                    'type': 'internal',
                    'edge': edge
                }
            )
        else:
            if _from['type'] not in MAKE_BRIDGE and to['type'] in MAKE_BRIDGE:
                bridge_name = name + '_' + to['type'] + '_' + str(to['id'])
                bridges[bridge_name]['objs'].append(_from)
            elif _from['type'] in MAKE_BRIDGE and to['type'] not in MAKE_BRIDGE:
                bridge_name = name + '_' + \
                    _from['type'] + '_' + str(_from['id'])
                bridges[bridge_name]['objs'].append(to)

    pp = pprint.PrettyPrinter(indent=4)

    print(pp.pprint(bridges))
