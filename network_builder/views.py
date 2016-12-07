from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from network_builder.models import NetworkBuild


# Create your views here.
def create_topology(request):
    return render(request, 'topoly_builder.html', {'available_networks':
                                                   NetworkBuild.objects.all()})


@csrf_exempt
def save_network(request):
    net, _ = NetworkBuild.objects.get_or_create(name=request.POST.get('name'))
    net.text = request.POST.get('network')
    net.save()
    return HttpResponse("ok")


@csrf_exempt
def network_load(request):
    net = get_object_or_404(NetworkBuild, name=request.POST.get('name'))
    return HttpResponse(net.text)
