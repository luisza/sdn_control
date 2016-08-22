# encoding: utf-8

'''
Free as freedom will be 21/8/2016

@author: luisza
'''

from __future__ import unicode_literals
from sdnctl.device.sshclient import SSHConnection
from sdnctl.device.DHCP import DHCP


def dhcp_action_up(modeladmin, request, queryset):
    for dhcp in queryset:
        server = DHCP(dhcp,
                      SSHConnection(dhcp.bridge.ovs.administrative_ip))
        server.create_dhcp_server()
dhcp_action_up.short_description = "Create dhcp server form network"


def dhcp_action_down(modeladmin, request, queryset):
    for dhcp in queryset:
        server = DHCP(dhcp,
                      SSHConnection(dhcp.bridge.ovs.administrative_ip))
        server.del_dhcp_server()
dhcp_action_down.short_description = "Delete dhcp server form network"


def dhcp_action_restart(modeladmin, request, queryset):
    for dhcp in queryset:
        server = DHCP(dhcp,
                      SSHConnection(dhcp.bridge.ovs.administrative_ip))
        server.del_dhcp_server()
        server.create_dhcp_server()
dhcp_action_restart.short_description = "Restart dhcp server form network"
