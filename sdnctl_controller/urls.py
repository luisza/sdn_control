from django.conf.urls import url

from views import create_sdn_controller, delete_sdn_controller, restart_sdn_controller


urlpatterns = [
    url(r'^controller/create/(?P<pk>\d+)$', create_sdn_controller),
    url(r'^controller/delete/(?P<pk>\d+)$', delete_sdn_controller),
    url(r'^controller/restart/(?P<pk>\d+)$', restart_sdn_controller)
]
