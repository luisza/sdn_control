from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from sdnctl.model_logic import NICLogic, HostLogic, RouteLogic,\
    Logical_NIC_control

# Create your models here.


@python_2_unicode_compatible
class OVS(models.Model):
    name = models.CharField(max_length=256, default="OVS")
    control_ip = models.GenericIPAddressField()
    controller_url = models.CharField(max_length=256,
                                      help_text="127.0.0.1:6633",
                                      default="127.0.0.1:6633"
                                      )
    administrative_ip = models.GenericIPAddressField()
    ignore_bridge = models.CharField(
        max_length=256,
        help_text="coma separated name ej br0,br1",
        null=True, blank=True)

    def __str__(self):
        return self.control_ip


@python_2_unicode_compatible
class NetworkBridge(models.Model):
    ovs = models.ForeignKey(OVS)

    name = models.CharField(max_length=10)
    base_ip = models.GenericIPAddressField()
    netmask = models.CharField(max_length=33)
    broadcast = models.GenericIPAddressField()

    def __str__(self):
        return "Bridge %s --> %s addr: %s netmask: %s broadcast: %s" % (
            self.ovs.control_ip,
            self.name,
            self.base_ip,
            self.netmask,
            self.broadcast
        )


class BridgeLink(models.Model):
    base = models.ForeignKey(
        NetworkBridge,
        related_name="base")

    related_bridges = models.ManyToManyField(
        NetworkBridge,
        related_name="related_bridges"
    )


@python_2_unicode_compatible
class Host(models.Model, HostLogic):
    mac = models.CharField(max_length=100)

    def __str__(self):
        nic = self.get_control_nic()
        if nic is None:
            return "Machine lost, no default NIC"

        return "Host %s control addr: %s netmask: %s broadcast: %s" % (
            self.mac,
            nic.address,
            nic.netmask,
            nic.broadcast
        )


@python_2_unicode_compatible
class Route(models.Model, RouteLogic):
    network = models.GenericIPAddressField()
    netmask = models.CharField(max_length=3,
                               default="/24",
                               help_text="abrev mode ej. /24")
    via = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        via = ""
        if self.via:
            via = "via %s" % (self.via)
        return "Route  %s%s %s dev <iface>" % (
            self.network,
            self.netmask,
            via)


@python_2_unicode_compatible
class NIC(models.Model, NICLogic):
    host = models.ForeignKey(Host)

    interface = models.CharField(max_length=10)
    address = models.GenericIPAddressField(null=True, blank=True)
    netmask = models.CharField(max_length=33, null=True, blank=True)
    broadcast = models.GenericIPAddressField(null=True, blank=True)
    default_gw = models.BooleanField(default=False)
    is_control = models.BooleanField(default=False)

    routes = models.ManyToManyField(Route)

    def __str__(self):
        return "NIC %s addr: %s netmask %s broadcast %s" % (
            self.interface,
            self.address,
            self.netmask,
            self.broadcast
        )


@python_2_unicode_compatible
class Logical_NIC(NIC, Logical_NIC_control):
    bridge = models.ForeignKey(NetworkBridge)
    is_dhcp = models.BooleanField(default=False)
    key = models.SmallIntegerField(default=1)

    def __str__(self):
        return "Logical NIC %s addr: %s netmask %s broadcast %s" % (
            self.interface,
            self.address,
            self.netmask,
            self.broadcast
        )

    def get_iface_info(self):
        return Logical_NIC_control.get_iface_info(self)
