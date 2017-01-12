# encoding: utf-8


'''
Created on 4/1/2017

@author: luisza
'''
from __future__ import unicode_literals

import ConfigParser
import os
from sdnctl.models import OVS, SDNController, RyuApp


def _load_ovs(config, ovs):
    ovs, _ = OVS.objects.get_or_create(
        name=config.get(ovs, 'name'),
        control_ip=config.get(ovs, 'control_ip'),
        administrative_ip=config.get(ovs, 'administrative_ip')
    )


def load_ovs(config):
    try:
        defaultovs = config.get('web', 'default_ovs').split(",")
        for ovs in defaultovs:
            _load_ovs(config, ovs)
    except:
        pass


def load_sdncontroller(controller, config):
    cont, created = SDNController.objects.get_or_create(
        name=config.get(controller, 'name'),
        control_ip=config.get(controller, 'control_ip'),
        ip=config.get(controller, 'ip'),
        port=config.get(controller, 'port'),
        apps_type=config.get(controller, 'apps_type'),
        wsapi_host=config.get(controller, 'wsapi_host'),
        wsapi_port=config.get(controller, 'wsapi_port')
    )
    if created:
        apps = config.get(controller, 'apps').split(',')
        for app in apps:
            n = app.split(".")[-1]
            a, _ = RyuApp.objects.get_or_create(
                name=n,
                app_code=app

            )
            cont.apps.add(a)
        cont.save()


def _load_sdncontrollers(config):
    defaultcontroller = config.get('web', 'default_controller')
    if defaultcontroller:
        defaultcontroller = defaultcontroller.split(',')
        for controller in defaultcontroller:
            try:
                load_sdncontroller(controller, config)
            except:
                pass


def load_sdncontrollers(config):
    try:
        _load_sdncontrollers(config)
    except:
        pass


config = ConfigParser.ConfigParser({'service': 'all'})

home = os.environ['HOME']

if os.path.exists("/etc/sdnctl/sdnctl.conf"):
    config.read("/etc/sdnctl/sdnctl.conf")

if os.path.exists(home + "/.sdnctl.conf"):
    config.read(home + "/.sdnctl.conf")

_type = config.get('control', 'service')

if "web" in _type:
    load_ovs(config)
    load_sdncontrollers(config)
if 'hipervisor' in _type:
    SASL_USER = config.get('hipervisor', 'libvirt_user')
    SASL_PASS = config.get('hipervisor', 'libvirt_password')
