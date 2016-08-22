from django.contrib import admin
from sdnctl import models
from sdnctl.actions.HostActions import host_action_restart
from sdnctl.actions.OVSActions import ovs_action_restart
from sdnctl.actions.DHCPAction import dhcp_action_down, dhcp_action_up,\
    dhcp_action_restart

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
    actions = [host_action_restart]


class DHCP_static_IPAdmin(admin.StackedInline):
    model = models.DHCP_Static_IP
    extra = 0


class DHCPServerAdmin(admin.ModelAdmin):
    inlines = [DHCP_static_IPAdmin]
    actions = [dhcp_action_up, dhcp_action_down,
               dhcp_action_restart]

admin.site.register(models.OVS, OVSAdmin)
admin.site.register(models.Host, HostAdmin)
admin.site.register(models.Route)
admin.site.register(models.BridgeLink)
admin.site.register(models.DHCP_Server, DHCPServerAdmin)
