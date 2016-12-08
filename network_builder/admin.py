from django.contrib import admin
from network_builder import models
# Register your models here.

admin.site.register(models.NetworkBuild)
admin.site.register(models.Link)


class RouterAddressAdmin(admin.TabularInline):
    model = models.RouterAddress
    extra = 1


class NetworkAdmin(admin.TabularInline):
    model = models.Network
    extra = 1


class RouterAdmin(admin.ModelAdmin):
    inlines = [NetworkAdmin, RouterAddressAdmin]


class RulesAdmin(admin.TabularInline):
    model = models.FirewallRule
    extra = 1


class FirewallAdmin(admin.ModelAdmin):
    inlines = [RulesAdmin]

admin.site.register(models.Router, RouterAdmin)
admin.site.register(models.Firewall, FirewallAdmin)
