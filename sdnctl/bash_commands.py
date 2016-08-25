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
BASH_DEL_PORT = SUDO + "ovs-vsctl del-port  %(br_name)s %(port_name)s; "
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
BASH_DEL_LINK = SUDO + "ip link del %s; "
BASH_HOST_FILE_PATH = "/var/run/sdndhcp/hostfile_%d.conf"
BASH_CREATE_RUN_DIR = SUDO + "mkdir -p /var/run/sdndhcp || true; "
BASH_CREATE_HOSTFILE = SUDO + 'echo "%s" %s /var/run/sdndhcp/hostfile_%d.conf;'

DHCP_PID = "/var/run/sdndhcp/hostfile_%d.pid"
# FIXME terminar
BASH_DHCP = BASH_CREATE_RUN_DIR + SUDO + "ip link add name %(iface)s type veth peer name peer_%(iface)s; \
" + SUDO + "ip link set dev %(iface)s up; " + SUDO + \
    SUDO + "ip link set dev peer_%(iface)s up; " + \
    SUDO + "ifconfig %(iface)s %(address)s %(netmask)s %(broadcast)s; "+SUDO + \
    "dnsmasq --no-hosts --no-resolv %(host_file)s --pid-file=%(pid)s --log-facility=/var/log/dnsdhcp_%(iface)s.log --interface=%(iface)s --dhcp-range=%(dhcp_range)s --listen-address=%(address)s --bind-interfaces; "

BASH_KILL_PROGRAM = SUDO + "kill -9 ´cat %s´; "
