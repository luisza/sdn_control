from django.contrib import admin
from network_builder.models import NetworkBuild, Network, Router, RouterAddress

# Register your models here.

admin.site.register(NetworkBuild)


class RouterAddressAdmin(admin.TabularInline):
    model = RouterAddress
    extra = 1


class NetworkAdmin(admin.TabularInline):
    model = Network
    extra = 1


class RouterAdmin(admin.ModelAdmin):
    inlines = [NetworkAdmin, RouterAddressAdmin]

admin.site.register(Router, RouterAdmin)
