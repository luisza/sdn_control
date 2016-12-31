from django.contrib import admin

from sdnctl import models
from sdnctl.actions.HostActions import host_action_restart
from sdnctl.actions.OVSActions import ovs_action_restart
from sdnctl.actions.RYUAction import ryu_action_up, ryu_action_down


# Register your models here.
# class NetworkBridgeInline(admin.TabularInline):
#     model = models.NetworkBridge
#     extra = 1


class OVSAdmin(admin.ModelAdmin):
    #     inlines = [NetworkBridgeInline]
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

#
# class Logical_NICInline(admin.StackedInline):
#     model = models.Logical_NIC
#     extra = 0


class HostAdmin(admin.ModelAdmin):
    inlines = [NICInline, ]  # Logical_NICInline]
    actions = [host_action_restart]


class SDNControlAdmin(admin.ModelAdmin):
    list_display = ('name', 'control_ip', 'ip', 'port', 'get_apps')
    readonly_fields = ('get_apps', )
    filter_horizontal = ('apps',)
    actions = [ryu_action_up, ryu_action_down]
#     inlines = [NetworkBridgeInline]

admin.site.register(models.OVS, OVSAdmin)
admin.site.register(models.Host, HostAdmin)
admin.site.register(models.Route)
# admin.site.register(models.BridgeLink)
admin.site.register(models.SDNController, SDNControlAdmin)
admin.site.register(models.RyuApp)
