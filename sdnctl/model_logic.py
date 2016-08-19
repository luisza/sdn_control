# encoding: utf-8

'''
Free as freedom will be 14/8/2016

@author: luisza
'''

from __future__ import unicode_literals
from django.utils.deconstruct import deconstructible


@deconstructible
class NICLogic(object):

    def get_routes(self, routes=[]):

        if self.default_gw:
            routes.append(
                          {'net': 'default', 'dev': self.interface}
                          )

        for route in self.routes.all():
            route_info = route.get_info()
            route_info['dev'] = self.interface
            routes.append(route_info)

        return routes

    def get_iface_info(self):
        return {'iface': self.interface,
                'addr': self.address,
                'netmask': self.netmask,
                'broadcast': self.broadcast}


@deconstructible
class Logical_NIC_control(object):

    def get_tunnel_info(self):
        ctrl_nic = self.host.get_control_nic()
        if ctrl_nic is None:
            # FIXME:que pasa aqui
            return
        return {'ip_local': ctrl_nic.address,
                'ip_remote': self.bridge.ovs.control_ip,
                'key': self.key,
                'iface': self.interface
                }

    def get_iface_info(self):
        if self.is_dhcp:
            return None
        if self.address is None:
            return None

        dev = {'iface': self.interface,
               'addr': self.address,
               'netmask': self.netmask,
               'broadcast': self.broadcast}
        if dev['netmask'] is None:
            dev['netmask'] = self.bridge.netmask
        if dev['broadcast'] is None:
            dev['broadcast'] = self.bridge.broadcast

        return dev


@deconstructible
class HostLogic(object):

    def get_host_info(self):
        host_info = {
            'dev_iface': [],
            'dev_tunnel': [],
            'route': []
        }
        for nic in self.nic_set.all().order_by('default_gw'):
            nic.get_routes(routes=host_info['route'])
            if hasattr(nic, 'logical_nic'):
                info = nic.logical_nic.get_iface_info()
                if info is not None:
                    host_info['dev_iface'].append(info)

                host_info['dev_tunnel'].append(
                    nic.logical_nic.get_tunnel_info())
            else:
                host_info['dev_iface'].append(
                    nic.get_iface_info())

        return host_info

    def get_control_nic(self):
        dev = self.nic_set.all().filter(is_control=True)
        if len(dev) >= 1:
            return dev[0]
        return None


@deconstructible
class RouteLogic(object):

    def get_info(self):
        dev = {'net': self.network + self.netmask}
        if self.via:
            dev['via'] = self.via
        return dev
