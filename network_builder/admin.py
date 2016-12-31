from django.contrib import admin
from network_builder import models
# Register your models here.

admin.site.register(models.NetworkBuild)


class RouterAddressAdmin(admin.TabularInline):
    model = models.RouterAddress
    extra = 1


class NetworkAdmin(admin.TabularInline):
    model = models.Network
    extra = 1


class RouterAdmin(admin.ModelAdmin):
    inlines = [NetworkAdmin, RouterAddressAdmin]
    exclude = ['network_instance', 'switch_id', 'bridge']


class RulesAdmin(admin.TabularInline):
    model = models.FirewallRule
    extra = 1


class DHCP_static_IPAdmin(admin.StackedInline):
    model = models.DHCP_Static_IP
    extra = 0


class DHCPAdmin(admin.ModelAdmin):
    inlines = [DHCP_static_IPAdmin]
    exclude = ['network_instance', 'bridge']


class FirewallAdmin(admin.ModelAdmin):
    inlines = [RulesAdmin]
    exclude = ['network_instance', 'switch_id', 'bridge']


class LinkAdmin(admin.ModelAdmin):
    list_display = ('address', 'mac', 'is_dhcp')


admin.site.register(models.Router, RouterAdmin)
admin.site.register(models.Firewall, FirewallAdmin)
admin.site.register(models.DHCP, DHCPAdmin)
admin.site.register(models.Link, LinkAdmin)
admin.site.register([models.Host, models.MachineImage])
