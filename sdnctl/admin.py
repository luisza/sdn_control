from django.contrib import admin
from sdnctl import models
from sdnctl.device.OVS import ovs_action_restart

# Register your models here.


class NetworkBridgeInline(admin.TabularInline):
    model = models.NetworkBridge
    extra = 1


class OVSAdmin(admin.ModelAdmin):
    inlines = [NetworkBridgeInline]
    actions = [ovs_action_restart]


class NICInline(admin.StackedInline):
    model = models.NIC
    extra = 0

    def get_queryset(self, request):
        nics = admin.StackedInline.get_queryset(self, request)
        exclude = []
        for nic in nics:
            if hasattr(nic, 'logical_nic'):
                exclude.append(nic.pk)
        return nics.exclude(pk__in=exclude)


class Logical_NICInline(admin.StackedInline):
    model = models.Logical_NIC
    extra = 0


class HostAdmin(admin.ModelAdmin):
    inlines = [NICInline, Logical_NICInline]

admin.site.register(models.OVS, OVSAdmin)
admin.site.register(models.Host, HostAdmin)
admin.site.register(models.Route)
admin.site.register(models.BridgeLink)
