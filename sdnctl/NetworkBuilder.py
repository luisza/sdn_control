# encoding: utf-8


'''
Created on 3/1/2017

@author: luisza
'''
from __future__ import unicode_literals

import copy
import json
import pprint

from network_builder import orchestra
from network_builder.models import Link, NetworkBridge, BridgeLink, Host,\
    MachineImage
from network_builder.utils import get_natural_name, DJOBJS, MAKE_BRIDGE,\
    get_apps
from sdnctl import settings
from sdnctl.models import OVS, SDNController, RyuApp


def get_control_ip(queryset):
    first = queryset.first()
    control_ip = "127.0.0.1"
    if first:
        control_ip = first.control_ip
    return control_ip


def get_controller(name, apps, _type):

    obj = SDNController.objects.filter(  # name="controller_" + name,
        apps_type=_type).first()
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


def create_django_link(edge, net, bridge):
    link = Link.objects.create(is_dhcp=True,
                               bridge=bridge,
                               network_instance=net)
    return link


def get_django_object(node, net):
    if 'djvalue' in node and node['type'] in DJOBJS:
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
    return nb


def set_bridge(bridge, obj, data):
    if hasattr(obj, 'bridge'):
        obj.bridge = bridge
        obj.save()


def connect_bridge(_from, to, bridges, net):

    blink, _ = BridgeLink.objects.get_or_create(
        base=_from, network_instance=net)
    rel = blink.related_bridges.filter(pk=to.pk).first()
    if rel is None:
        blink.related_bridges.add(to)
        blink.save()
    return blink


def update_object_link(_type, node, link, net, bridge):
    obj = link['obj']
    if 'from' == _type:
        obj.from_obj = node['obj'].pk
        obj.from_naturalname = get_natural_name(node['obj'])
    else:
        obj.to_obj = node['obj'].pk
        obj.to_naturalname = get_natural_name(node['obj'])
    obj.network_instance = net
    obj.bridge = bridge
    obj.save()


def get_machine_imagen():
    image = MachineImage.objects.first()
    if not image:
        image = MachineImage.objects.create()
    return image


def create_djobject_from_node(node, net):
    device = None
    if node['type'] == 'host':
        device = Host.objects.create(network_instance=net,
                                     image=get_machine_imagen())

    return device


def extract_nodes(edges, data, way):
    """
    Extract nodes from edges list,
    way is 'to' or 'from'
    """
    dev = []
    for bg in edges:
        nnode = list(filter(lambda x: x['id'] == bg[way], data['nodes']))
        if nnode:
            nnode = nnode[0]
            if nnode['type'] in MAKE_BRIDGE:
                bg['type'] = 'internaledge'
            else:
                bg['type'] = 'edge'
                dev.append(nnode)
            dev.append(bg)
    return dev


def extract_bridges(data):
    """ 
    Create a bridges and match nodes related
    A bridge is a list of nodes and edges that
    would be aprovisionated in the ovs bridge
    """
    bridges = {}
    for node in data['nodes']:
        if node['type'] in MAKE_BRIDGE:
            id = node['id']
            bridges[id] = [node]

            to = filter(lambda x: x['to'] == id, data['edges'])
            _from = filter(lambda x: x['from'] == id, data['edges'])
            bridges[id] += extract_nodes(to, data, 'from')
            bridges[id] += extract_nodes(_from, data, 'to')
    return bridges


def process_internal_edge(node, bridges, net, name, bridge):
    dev = None
    if node['type'] == 'internaledge':
        to = "n%d_%d" % (net.pk, node['to'])
        _from = "n%d_%d" % (net.pk, node['from'])
        dev = connect_bridge(bridges[_from]['obj'],
                             bridges[to]['obj'],
                             bridges, net)
    return dev


def process_edge(edges, name, bridge, objs, net):
    dev = []
    for node in edges:
        print(node)
        if node['type'] == 'edge':
            if 'obj' not in node:
                node['obj'] = create_django_link(node, net, bridge)
                node['djvalue'] = node['obj'].pk

            if node['from'] == name:  # node is from
                to = list(filter(lambda x: x['id'] == node['to'], objs))
                if to:

                    update_object_link('to', to[0], node, net, bridge)
            else:  # node is to
                _from = list(
                    filter(lambda x: x['id'] == node['from'], objs))
                if _from:
                    update_object_link('from', _from[0], node, net, bridge)

            dev.append(node)
    return dev


def proccess_bridge_children(bridges, net, name, bridge, children):
    dev = []
    edges = []
    for node in children:
        obj = get_django_object(node, net)
        if not obj:  # Check if can create automatic node
            obj = create_djobject_from_node(node, net)
        if not obj:  # Check if it is a link
            obj = process_internal_edge(node, bridges, net, name, bridge)
        if not obj:  # maybe edges
            edges.append(node)
            continue
        node['djvalue'] = obj.pk
        node['obj'] = obj
        if node['type'] == 'edge':
            edges.append(node)
        else:
            set_bridge(bridge, obj, None)
            dev.append(node)

    dev += process_edge(edges, name, bridge, dev, net)
    return dev


def find_idnode(node, id):
    for i, obj in enumerate(node):
        if obj['id'] == id:
            return i


def update_object_id_in_data(data, bridges):
    for bridge in bridges:
        for node in bridges[bridge]['children']:
            if node['type'] == 'internaledge':
                continue
            if node['type'] == 'edge':
                _type = 'edges'
            else:
                _type = 'nodes'
            pos = find_idnode(data[_type], node['id'])
            if pos:
                data[_type][pos]['djvalue'] = node['djvalue']
    return data


def build_tree_network(data, name, net):
    data_safe = copy.deepcopy(data)
    ref_bridges = extract_bridges(data)
    bridges = {}
    for bridge in ref_bridges:
        bg_name = "n%d_%d" % (net.pk, bridge)
        controller = get_controller(bg_name, get_apps([
            ref_bridges[bridge][0]
        ]), ref_bridges[bridge][0]['type'])
        bridges[bg_name] = {
            'obj': get_bridge(bg_name, net, controller=controller)}

    for bridge in ref_bridges:
        bg_name = "n%d_%d" % (net.pk, bridge)
        bridges[bg_name]['children'] = proccess_bridge_children(
            bridges,
            net,
            bridge,
            bridges[bg_name][
                'obj'],
            ref_bridges[bridge])
    data_safe = update_object_id_in_data(data_safe, bridges)
#     pp = pprint.PrettyPrinter(indent=2)
#     pp.pprint(data_safe)
    return bridges, net, data_safe


def process_tree_network(tree, net):
    ovss = []
    for bridge in tree:
        orchestra.start_controller(net.pk,
                                   tree[bridge]['obj'].controller)
        obj = tree[bridge]['obj']
        obj.get_name()
        ovs = tree[bridge]['obj'].ovs
        if not ovs in ovss:
            ovss.append(ovs)
    for ovs in ovss:
        orchestra.create_bridges(net.pk, ovs)


def build_network(data, name, net):
    #     pp = pprint.PrettyPrinter(indent=2)
    #     pp.pprint(data)
    #     print("\n" * 6)
    tree, net, data = build_tree_network(data, name, net)
    net.text = json.dumps(data)
    net.save()
    process_tree_network(tree, net)
