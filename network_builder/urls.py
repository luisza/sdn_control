# encoding: utf-8

'''
Free as freedom will be 6/12/2016

@author: luisza
'''

from __future__ import unicode_literals
from django.conf.urls import url

from network_builder import views

urlpatterns = [

    url(r'^topology$', views.create_topology),
    url(r'^network/save$', views.save_network, name="network_save"),
    url(r'network/load$', views.network_load, name="network_load")
]
