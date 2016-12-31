from __future__ import unicode_literals

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
import uuid

from sdnctl.models import OVS, SDNController


# Create your models here.
class NetworkBuild(models.Model):
    name = models.CharField(max_length=250, default="mynetwork")
    text = models.TextField()


@python_2_unicode_compatible
class NetworkBridge(models.Model):
    name = models.CharField(max_length=250, default="br0")
    ovs = models.ForeignKey(OVS)
    controller = models.ForeignKey(SDNController, null=True, blank=True)
    network_instance = models.ForeignKey(NetworkBuild, null=True, blank=True)

    def get_name(self):

        if self.network_instance:
            return "n%d_%d" % (self.network_instance.pk, self.pk)
        return self.name

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class BridgeLink(models.Model):
    base = models.ForeignKey(
        NetworkBridge,
        related_name="base")

    related_bridges = models.ManyToManyField(
        NetworkBridge,
        related_name="related_bridges"
    )
    network_instance = models.ForeignKey(NetworkBuild, null=True, blank=True)

    def __str__(self):
        return str(self.base) + "-> " + ", ".join([str(x) for x in self.related_bridges.all()])


@python_2_unicode_compatible
class Router(models.Model):
    name = models.CharField(
        max_length=250, default="router", null=True, blank=True)
    switch_id = models.CharField(max_length=20, null=True, blank=True)
    network_instance = models.ForeignKey(NetworkBuild, null=True, blank=True)
    bridge = models.ForeignKey(NetworkBridge, null=True, blank=True)

    def __str__(self):
        return self.name


class RouterAddress(models.Model):
    address = models.CharField(max_length=250, null=True, blank=True,
                               help_text="127.0.0.1/24")
    router = models.ForeignKey(Router)


class Network(models.Model):
    network = models.CharField(max_length=250)
    gateway = models.GenericIPAddressField()
    router = models.ForeignKey(Router)


@python_2_unicode_compatible
class Firewall(models.Model):
    name = models.CharField(
        max_length=250, default="Firewall", null=True, blank=True)
    switch_id = models.CharField(max_length=20, null=True, blank=True)
    network_instance = models.ForeignKey(NetworkBuild, null=True, blank=True)
    bridge = models.ForeignKey(NetworkBridge, null=True, blank=True)

    def __str__(self):
        return self.name


class FirewallRule(models.Model):
    priority = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(65535)],
        default=1)
    dl_src = models.CharField(max_length=50, null=True, blank=True,
                              help_text="xx:xx:xx:xx:xx:xx",
                              verbose_name="Source MAC")
    dl_dst = models.CharField(max_length=50, null=True, blank=True,
                              help_text="xx:xx:xx:xx:xx:xx",
                              verbose_name="Destination MAC")
    dl_type = models.CharField(max_length=5,
                               choices=(("ARP", "ARP"), ("Ipv4", "Ipv4")),
                               default="Ipv4"
                               )
    nw_src = models.CharField(max_length=50, null=True, blank=True,
                              help_text="xxx.xxx.xxx.xxx/xx",
                              verbose_name="Source Address")

    nw_dst = models.CharField(max_length=50, null=True, blank=True,
                              help_text="xxx.xxx.xxx.xxx/xx",
                              verbose_name="Destination Address")

    nw_proto = models.CharField(max_length=7, null=True, blank=True,
                                choices=(
                                    ("TCP", "TCP"),
                                    ("UDP", "UDP"),
                                    ("ICMP", "ICMP"),
                                    ("ICMPv6", "ICMPv6")),
                                verbose_name="Protocol"
                                )
    tp_src = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(65535)],
        verbose_name="Source Port")

    tp_dst = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(65535)],
        verbose_name="Destination Port")

    actions = models.CharField(max_length=6,
                               choices=(("ALLOW", "ALLOW"), ("DENY", "DENY"))
                               )

    firewall = models.ForeignKey(Firewall)


@python_2_unicode_compatible
class Link(models.Model):

    is_dhcp = models.BooleanField(default=True)
    mac = models.CharField(max_length=50, null=True, blank=True,
                           help_text="xx:xx:xx:xx:xx:xx",
                           verbose_name="Source MAC")
    address = models.GenericIPAddressField(null=True, blank=True)
    netmask = models.CharField(max_length=33,
                               default="255.255.255.0",
                               null=True, blank=True)
    broadcast = models.GenericIPAddressField(null=True, blank=True)
    speed = models.IntegerField(default=100, help_text="MB")

    from_obj = models.IntegerField(default=0)
    from_naturalname = models.CharField(
        max_length=250, default="network_builder.Router")
    to_obj = models.IntegerField(default=0)
    to_naturalname = models.CharField(
        max_length=250, default="network_builder.Host")

    def __str__(self):
        return "%s %s" % (self.address, str(self.is_dhcp))


@python_2_unicode_compatible
class DHCP(models.Model):
    start_ip = models.GenericIPAddressField()
    end_ip = models.GenericIPAddressField()
    lease_time = models.CharField(max_length=10,
                                  default="infinite")

    network_instance = models.ForeignKey(NetworkBuild, null=True, blank=True)
    bridge = models.ForeignKey(NetworkBridge, null=True, blank=True)

    def __str__(self):
        return "%s,%s" % (
            self.start_ip,
            self.end_ip
        )


class DHCP_Static_IP(models.Model):
    dhcp_server = models.ForeignKey(DHCP)
    mac = models.CharField(max_length=100)
    address = models.GenericIPAddressField()
    hostname = models.CharField(max_length=33, null=True, blank=True)

    lease_time = models.CharField(max_length=10,
                                  default="infinite",
                                  help_text="03m/infinite/ignore")


class MachineImage(models.Model):
    name = models.CharField(
        max_length=250, default="Cirros x86_64", null=True, blank=True)
    path = models.CharField(
        max_length=250, default="/var/lib/libvirt/images/cirros-0.3.4-x86_64-disk.img", null=True, blank=True)


class Host(models.Model):
    name = models.CharField(
        max_length=250, default="Host", null=True, blank=True)
    network_instance = models.ForeignKey(NetworkBuild, null=True, blank=True)
    bridge = models.ForeignKey(NetworkBridge, null=True, blank=True)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    memory = models.IntegerField(default=256000)
    vcpu = models.SmallIntegerField(default=1)
    architecture = models.CharField(max_length=25,
                                    default='x86_64',
                                    choices=(('x86_64', 'x86_64'),
                                             ('i386', 'x86')))
    image = models.ForeignKey(MachineImage, null=True)

    def __str__(self):
        return self.name
