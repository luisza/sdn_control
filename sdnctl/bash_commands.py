# encoding: utf-8

'''
Free as freedom will be 18/8/2016

@author: luisza
'''

from __future__ import unicode_literals

SUDO = "sudo "
BASH_ADD_BRIDGE = SUDO + "ovs-vsctl add-br %(name)s; " + SUDO + "\
ip link set %(name)s up multicast on mtu 1420; " + SUDO + "\
ovs-vsctl set-controller %(name)s tcp:%(controller_url)s; "
BASH_DEL_BRIDGE = SUDO + "ovs-vsctl del-br %s; "
BASH_SHOW_BRIDGE = SUDO + 'ovs-vsctl show | grep "Bridge"'
BASH_ADD_INTERNAL_PORT = SUDO + \
    'ovs-vsctl add-port %(br_name)s %(port_name)s; '
BASH_ADD_PORT = SUDO + "ovs-vsctl add-port %(br_name)s %(port_name)s \
 -- set interface %(port_name)s type=gre options:key=%(key)s \
 options:remote_ip=%(remote_ip)s; "
BASH_ADD_OVS_PORT = SUDO + "ovs-vsctl add-port %(name)s %(br_name)s \
-- set interface %(br_name)s type=gre options:remote_ip=%(remote_ip)s; "
BASH_SET_IP = SUDO + \
    "ip addr add %(cidr)s broadcast %(broadcast)s dev %(iface)s; "
