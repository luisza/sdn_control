from django.http.response import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404

from sdnctl.models import Host


# Create your views here.
def get_host_info(request):
    host_mac = request.GET.get('mac')
    if not host_mac:
        raise Http404()
    host = get_object_or_404(Host, mac=host_mac)
    return JsonResponse(host.get_host_info())
