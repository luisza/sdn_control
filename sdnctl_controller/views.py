# encoding: utf-8


'''
Created on 9/12/2016

@author: luisza
'''
from __future__ import unicode_literals

from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from sdnctl.device.RYUController import RyuController
from sdnctl.models import SDNController
from sdnctl.shell.bashclient import BashClient as bashclient


def create_sdn_controller(request, pk):

    instance = get_object_or_404(SDNController, pk=pk)
    bash = bashclient()
    ctl = RyuController(instance, bash)
    ctl.start()
    return HttpResponse("OK")


def delete_sdn_controller(request, net, pk):
    instance = get_object_or_404(SDNController, pk=pk)
    bash = bashclient()
    ctl = RYUController(instance, bash)
    ctl.stop()
    return HttpResponse("OK")


def restart_sdn_controller(request, net, pk):
    instance = get_object_or_404(SDNController, pk=pk)
    bash = bashclient()
    ctl = RYUController(instance, bash)
    ctl.stop()
    ctl.start()
    return HttpResponse("OK")
