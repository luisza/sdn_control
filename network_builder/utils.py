# encoding: utf-8


'''
Created on 8/12/2016

@author: luisza
'''
from __future__ import unicode_literals

import copy
import json
import pprint
import random

from network_builder import orchestra
from network_builder.models import Host, Router, Firewall, Link, DHCP, NetworkBridge, BridgeLink,\
    MachineImage
from sdnctl.models import SDNController, RyuApp, OVS


MAKE_BRIDGE = ['router', 'nat', 'firewall', 'vpn']
DJOBJS = {
    'router': Router,
    'host': Host,
    'firewall': Firewall,
    'dhcp': DHCP,
    'edges': Link
}


RYUAPPS = {
    'router': ['ryu.app.rest_router', 'ryu.controller.ofp_handler', 'ryu.app.dpinfo'],
    'firewall': ['ryu.app.rest_firewall', 'ryu.controller.ofp_handler', 'ryu.app.dpinfo']
}


def get_natural_name(model):
    return model._meta.app_label + "." + model._meta.model_name


def get_apps(nodes):
    app_list = []
    for node in nodes:
        if node['type'] in RYUAPPS:
            app_list += RYUAPPS[node['type']]
    return app_list


def create_django_link(edge):
    link = Link.objects.create(is_dhcp=True)
    edge['djvalue'] = link.pk
    return edge


def get_control_ip(queryset):
    first = queryset.first()
    control_ip = "127.0.0.1"
    if first:
        control_ip = first.control_ip
    return control_ip


def get_controller(name, apps):

    obj = SDNController.objects.filter(name="controller_" + name).first()
    if obj is not None:
        return obj

    controller = SDNController.objects.all()
    control_ip = get_control_ip(controller)
    port = 6633
    hport = 8080

    for cnt in controller.filter(control_ip=control_ip):
        for cnt in controller:
            if hport < cnt.wsapi_port:
                hport = cnt.wsapi_port
            if port < cnt.port:
                port = cnt.port
    port += 1
    hport += 1
    control_obj = SDNController.objects.create(name="controller_" + name,
                                               control_ip=control_ip,
                                               ip="0.0.0.0",
                                               port=port,
                                               wsapi_host="0.0.0.0",
                                               wsapi_port=hport
                                               )
    for app in apps:
        ryuapp, _ = RyuApp.objects.get_or_create(app_code=app)
        control_obj.apps.add(ryuapp)

    return control_obj


def get_django_object(node, net):
    if 'djvalue' in node:
        obj = DJOBJS[node['type']].objects.filter(pk=node['djvalue']).first()
        if obj:
            if hasattr(obj, 'network_instance'):
                obj.network_instance = net
                obj.save()
        return obj


def get_ovs():
    obj = OVS.objects.first()
    if obj is None:
        obj = OVS.objects.create(
            name="automatic ovs",
            control_ip="127.0.0.1",
            administrative_ip="127.0.0.1"
        )
    return obj


def get_bridge(name, net, controller=None):
    ovs = get_ovs()

    nb = NetworkBridge.objects.filter(name=name, network_instance=net).first()
    if nb is None:
        nb = NetworkBridge.objects.create(
            ovs=ovs,
            name=name,
            controller=controller,
            network_instance=net
        )

    # FIXME: quitar nb.get_name()
    # nb.get_name()
    return nb


def set_bridge(bridge, obj, data):
    if 'obj' in bridge and hasattr(obj, 'bridge'):
        obj.bridge = bridge['obj']
        obj.save()


def connect_bridge(_from, to, bridges, net):

    blink, _ = BridgeLink.objects.get_or_create(
        base=bridges[_from]['obj'], network_instance=net)
    rel = blink.related_bridges.filter(pk=bridges[to]['obj'].pk).first()
    if rel is None:
        blink.related_bridges.add(bridges[to]['obj'])
        blink.save()
    return blink


def update_object_link(_type, node, link):
    obj = link['obj']
    if 'from' == _type:
        obj.from_obj = node['obj'].pk
        obj.from_naturalname = get_natural_name(node['obj'])
    else:
        obj.to_obj = node['obj'].pk
        obj.to_naturalname = get_natural_name(node['obj'])
    obj.save()


def get_random_mac():
    return "00:00:00:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )


def create_djobject_form_node(node, net):
    device = None
    if node['type'] == 'host':
        device = Host.objects.create(network_instance=net,
                                     image=MachineImage.objects.create())

    return device


def build_tree_network(data, name, net):
    data_safe = copy.deepcopy(data)
    bridges = {}
    for i, node in enumerate(data['nodes']):
        if 'djvalue' in node:
            data['nodes'][i]['obj'] = get_django_object(node, net)
        else:
            data['nodes'][i]['obj'] = create_djobject_form_node(node, net)
            data_safe['nodes'][i]['djvalue'] = data['nodes'][i]['obj'].pk
        node = data['nodes'][i]

        if node['type'] in MAKE_BRIDGE:
            bg_name = "n%d_%d" % (net.pk, data['nodes'][i]['obj'].pk)
            bridges[bg_name] = {
                'ports': [],
                'objs': [node],
                'controller': get_controller(bg_name, get_apps([node])),
                'node': node
            }

            bridges[bg_name]['obj'] = get_bridge(bg_name, net,
                                                 controller=bridges[bg_name]['controller'])

        if 'obj' in data['nodes'][i]:
            set_bridge(bridges[bg_name], data['nodes'][i]['obj'], data)

    for i, edge in enumerate(data['edges']):
        edge['type'] = 'edges'
        if 'djvalue' not in edge:
            edge = create_django_link(edge)
            data['edges'][i] = edge
            data_safe['edges'][i]['djvalue'] = edge['djvalue']
        data['edges'][i]['obj'] = get_django_object(edge, net)
        edge = data['edges'][i]

        to = list(filter(lambda x: x['id'] == edge['to'], data['nodes']))
        _from = list(filter(lambda x: x['id'] == edge['from'], data['nodes']))
        if len(to) == 0 or len(_from) == 0:
            continue
        to, _from = to[0], _from[0]  # just one possible

        if to['type'] in MAKE_BRIDGE and _from['type'] in MAKE_BRIDGE:
            #from_br = name + '_' + _from['type'] + '_' + str(_from['id'])
            #to_br = name + '_' + to['type'] + '_' + str(to['id'])

            #bg_name = "n%d_%d" % (net.pk, data['nodes'][i]['obj'].pk)
            from_br = "n%d_%d" % (net.pk, _from['obj'].pk)
            to_br = "n%d_%d" % (net.pk, to['obj'].pk)
            bridges[from_br]['ports'].append({'from': from_br,
                                              'to': to_br,
                                              'type': 'internal',
                                              'edge': edge,
                                              'obj': connect_bridge(from_br, to_br, bridges, net)
                                              }
                                             )

        else:
            if _from['type'] not in MAKE_BRIDGE and to['type'] in MAKE_BRIDGE:
                #name + '_' + to['type'] + '_' + str(to['id'])
                #bg_name = "n%d_%d" % (net.pk, data['nodes'][i]['obj'].pk)

                bridge_name = "n%d_%d" % (net.pk, to['obj'].pk)
                bridges[bridge_name]['objs'].append(_from)
                update_object_link('from', _from, edge)
            elif _from['type'] in MAKE_BRIDGE and to['type'] not in MAKE_BRIDGE:
                # bridge_name = name + '_' + \
                #    _from['type'] + '_' + str(_from['id'])

                bridge_name = "n%d_%d" % (net.pk, _from['obj'].pk)
                bridges[bridge_name]['objs'].append(to)
                update_object_link('to', to, edge)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(bridges)

    return bridges, net, data_safe
#     pp = pprint.PrettyPrinter(indent=4)
#     pp.pprint(bridges)


def process_tree_network(tree, net):
    for bridge in tree:
        orchestra.start_controller(net.pk, tree[bridge]['controller'])
        obj = tree[bridge]['obj']
        obj.get_name()
        ovs = tree[bridge]['obj'].ovs
        orchestra.create_bridges(net.pk, ovs, obj.pk)


def build_network(data, name, net):
    tree, net, data = build_tree_network(data, name, net)
    net.text = json.dumps(data)
    net.save()
    process_tree_network(tree, net)
