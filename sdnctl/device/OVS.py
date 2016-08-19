# encoding: utf-8

'''
Free as freedom will be 15/8/2016

@author: luisza
'''

from __future__ import unicode_literals
from sdnctl.device.sshclient import SSHConnection

import re
from sdnctl.models import BridgeLink
from sdnctl.bash_commands import (
    BASH_ADD_BRIDGE,
    BASH_DEL_BRIDGE,
    BASH_SHOW_BRIDGE,
    BASH_ADD_PORT,
    BASH_ADD_OVS_PORT
)


class OVSManager(object):
    instance = None

    def __init__(self, obj):
        self.instance = obj
        self._bash = SSHConnection(obj.administrative_ip)

    def get_bridges(self):
        result = self._bash.execute(BASH_SHOW_BRIDGE,
                                    allow_error=True)
        bridges = []
        for dev in re.findall('"\w+"', result.output):
            bridges.append(dev.replace('"', ""))
        return bridges

    def clean(self):
        bash_cmd = ""
        exclude = []
        if self.instance.ignore_bridge:
            exclude = self.instance.ignore_bridge.split(",")
        for bridge in self.get_bridges():
            if bridge not in exclude:
                bash_cmd += BASH_DEL_BRIDGE % (bridge)

        if bash_cmd:
            self._bash.execute(bash_cmd)

    def add_bridges(self):
        bash_cmd = ""
        for bridge in self.instance.networkbridge_set.all():
            bash_cmd += BASH_ADD_BRIDGE % (
                {'name': bridge.name,
                 'controller_url': self.instance.controller_url})
        if bash_cmd:
            self._bash.execute(bash_cmd)

    def add_bridge(self, name):
        bash_cmd = BASH_ADD_BRIDGE % (name, name)
        self._bash.execute(bash_cmd)

    def add_ports(self):
        bash_cmd = ""
        for bridge in self.instance.networkbridge_set.all():
            index = 0
            for nic in bridge.logical_nic_set.all():
                remote_ip = nic.host.get_control_nic().address
                bash_cmd += BASH_ADD_PORT % {
                    'br_name': bridge.name,
                    'port_name': "host%d" % (nic.pk),
                    'remote_ip': remote_ip,
                    'key': nic.key
                }
                index += 1
        self._bash.execute(bash_cmd)

    def add_internal_port_connections(self):
        bash_cmd = ""
        for bridge in self.instance.networkbridge_set.all():
            for bridgelink in BridgeLink.objects.filter(base=bridge):
                name = bridgelink.base.name
                for br_ext in bridgelink.related_bridges.all():
                    external_ip = br_ext.ovs.control_ip
                    br_name = "gre_%s_%s_%d" % (name,
                                                br_ext.name,
                                                bridgelink.pk)
                    bash_cmd += BASH_ADD_OVS_PORT % {
                        'name': name,
                        'br_name': br_name,
                        'remote_ip': external_ip
                    }
            for bridgelink in BridgeLink.objects.filter(
                    related_bridges=bridge):
                name = bridgelink.base.name
                br_name = "gre_%s_%s_%d" % (name,
                                            bridge.name,
                                            bridgelink.pk)
                bash_cmd += BASH_ADD_OVS_PORT % {
                    'name': name,
                    'br_name': br_name,
                    'remote_ip': bridgelink.base.ovs.control_ip
                }

        self._bash.execute(bash_cmd)


def ovs_action_restart(modeladmin, request, queryset):
    for ovs in queryset:
        ovsmanager = OVSManager(ovs)
        ovsmanager.clean()
        ovsmanager.add_bridges()
        ovsmanager.add_ports()
        ovsmanager.add_internal_port_connections()

    ovs_action_restart.short_description = "Restart OVS"
