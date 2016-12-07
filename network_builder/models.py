from __future__ import unicode_literals

from django.db import models

# Create your models here.


class NetworkBuild(models.Model):
    name = models.CharField(max_length=250, default="mynetwork")
    text = models.TextField()


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
