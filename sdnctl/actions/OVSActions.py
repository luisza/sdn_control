# encoding: utf-8

'''
Free as freedom will be 20/8/2016

@author: luisza
'''

from __future__ import unicode_literals
from sdnctl.device.OVS import OVSManager
from sdnctl.device.DHCP import DHCP
from sdnctl.models import DHCP_Server


def ovs_action_restart(modeladmin, request, queryset):
    for ovs in queryset:
        ovsmanager = OVSManager(ovs)
        ovsmanager.clean()
        ovsmanager.add_bridges()
        ovsmanager.add_ports()
        ovsmanager.add_internal_port_connections()

        for dhcp in DHCP_Server.objects.filter(bridge__ovs=ovs):
            server = DHCP(dhcp,
                          ovsmanager._bash)
            server.del_dhcp_server(allow_error=True)
            server.create_dhcp_server()
ovs_action_restart.short_description = "Restart OVS"
