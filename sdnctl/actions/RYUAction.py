# encoding: utf-8


'''
Created on 4/12/2016

@author: luisza
'''
from __future__ import unicode_literals
from sdnctl.device.RYUController import RyuController
from sdnctl.device.sshclient import SSHConnection


def ryu_action_up(modeladmin, request, queryset):
    for controller in queryset:
        server = RyuController(controller,
                               SSHConnection(controller.control_ip))
        server.start()
ryu_action_up.short_description = "Start ryu server"


def ryu_action_down(modeladmin, request, queryset):
    for controller in queryset:
        server = RyuController(controller,
                               SSHConnection(controller.control_ip))
        server.stop()
ryu_action_down.short_description = "Stop ryu server"