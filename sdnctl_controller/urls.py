from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^register/dp$', views.register_datapath),
    url(r'^unregister/dp$', views.unregister_datapath),
    url(r'^controller/create/(?P<pk>\d+)$', views.create_sdn_controller),
    url(r'^controller/delete/(?P<pk>\d+)$', views.delete_sdn_controller),
    url(r'^controller/restart/(?P<pk>\d+)$', views.restart_sdn_controller)
]
