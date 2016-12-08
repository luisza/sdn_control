from __future__ import unicode_literals

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


# Create your models here.
class NetworkBuild(models.Model):
    name = models.CharField(max_length=250, default="mynetwork")
    text = models.TextField()


@python_2_unicode_compatible
class Router(models.Model):
    name = models.CharField(
        max_length=250, default="router", null=True, blank=True)
    switch_id = models.CharField(max_length=20, null=True, blank=True)

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
