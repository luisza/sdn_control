# encoding: utf-8


'''
Created on 9/12/2016

@author: luisza
'''
from __future__ import unicode_literals

from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from network_builder.models import Firewall, Router
from sdnctl.device.Firewall import Firewall as CFirewall
from sdnctl.device.RYUController import RyuController
from sdnctl.device.Router import Router as CRouter
from sdnctl.models import SDNController
from sdnctl.shell.bashclient import BashClient as bashclient


def create_sdn_controller(request, pk):

    instance = get_object_or_404(SDNController, pk=pk)
    bash = bashclient()
    ctl = RyuController(instance, bash)
    ctl.start()
    return HttpResponse("OK")


@csrf_exempt
def register_datapath(request):
    code = request.POST.get('code')
    ports = request.POST.get('ports', '').split(';')
    if code:
        routers = Router.objects.filter(bridge__name__in=ports)
        firewalls = Firewall.objects.filter(bridge__name__in=ports)
        for route in routers:
            route.switch_id = code
            route.save()
            r = CRouter(route)
            r.setup()

        for firewall in firewalls:
            firewall.switch_id = code
            firewall.save()
            f = CFirewall(firewall)
            f.setup()
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
