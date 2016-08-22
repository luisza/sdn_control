# encoding: utf-8

'''
Free as freedom will be 20/8/2016

@author: luisza
'''

from __future__ import unicode_literals
from sdnctl.device.socketclient import SocketClient


def host_action_restart(modeladmin, request, queryset):
    for host in queryset:
        nic = host.get_control_nic()
        hostclient = SocketClient(nic.address)
        hostclient.execute("1")

host_action_restart.short_description = "Restart Host"
