# encoding: utf-8

'''
Free as freedom will be 21/8/2016

@author: luisza
'''

from __future__ import unicode_literals
from sdnctl.models import DHCP_Static_IP
from sdnctl.bash_commands import BASH_CREATE_HOSTFILE, BASH_HOST_FILE_PATH,\
    BASH_DHCP, BASH_ADD_INTERNAL_PORT, BASH_DEL_PORT, DHCP_PID,\
    BASH_KILL_PROGRAM, BASH_DEL_LINK, BASH_CREATE_RUN_DIR


class DHCP(object):

    def create_host_file(self):
        self._bash.execute(BASH_CREATE_RUN_DIR)
        static_ips = DHCP_Static_IP.objects.filter(
            dhcp_server=self.instance)
        txt_ips = ""
        for index, static_ip in enumerate(static_ips):
            line = static_ip.mac
            if static_ip.address:
                line += "," + static_ip.address
            if static_ip.hostname:
                line += "," + static_ip.hostname
            line += "," + static_ip.lease_time
            aling = ">>" if index else ">"
            txt_ips += BASH_CREATE_HOSTFILE % (
                line, aling,
                self.instance.pk
            )
        if txt_ips:
            self._bash.execute(txt_ips)
            return " --dhcp-hostsfile=" + BASH_HOST_FILE_PATH % (
                self.instance.pk)

        return ""

    def get_ip_address(self):
        address = ""
        if self.instance.address:
            address = self.instance.address
        else:
            octet = list(self.instance.start_ip.split("."))
            octet[-1] = "1"
            address = ".".join(octet)
        return address

    def create_dhcp_server(self):
        host_file = self.create_host_file()
        dhcp_range = "%s,%s" % (
            self.instance.start_ip, self.instance.end_ip
        )
        if self.instance.broadcast and self.instance.netmask:
            dhcp_range += ',static,%s,%s' % (
                self.instance.netmask,
                self.instance.broadcast
            )

        dhcp_range += "," + self.instance.lease_time

        bash_cmd = BASH_DHCP % {
            'iface': 'dhcp_%d' % self.instance.pk,
            'pid': DHCP_PID % self.instance.pk,
            'dhcp_range': dhcp_range,
            'host_file': host_file,
            'address': self.get_ip_address(),
            'netmask': 'netmask ' + self.instance.netmask
            if self.instance.netmask else "",
            'broadcast': 'broadcast ' + self.instance.broadcast
            if self.instance.broadcast else ""
        }

        bash_cmd += BASH_ADD_INTERNAL_PORT % {
            'br_name': self.instance.bridge.name,
            'port_name': 'peer_dhcp_%d' % (self.instance.pk)
        }

        self._bash.execute(bash_cmd)

    def del_dhcp_server(self):

        pid = DHCP_PID % self.instance.pk
        bash_cmd = BASH_KILL_PROGRAM % pid

        bash_cmd += BASH_DEL_PORT % {
            'br_name': self.instance.bridge.name,
            'port_name': 'peer_dhcp_%d' % (self.instance.pk)
        }
        vnetname = 'dhcp_%d' % (self.instance.pk)
        bash_cmd += BASH_DEL_LINK % vnetname
        self._bash.execute(bash_cmd)

    def __init__(self, instance, bash):
        self.instance = instance
        self._bash = bash
