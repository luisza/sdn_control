# encoding: utf-8


'''
Created on 30/12/2016

@author: luisza
'''
from __future__ import unicode_literals

from django.db.models.query_utils import Q
import libvirt
import os

from network_builder.models import Link
from network_builder.utils import get_natural_name, get_random_mac


BASE_XML = """
<domain type='qemu'>
  <name>%(name)s</name>
  <uuid>%(uuid)s</uuid>
  <memory unit='KiB'>%(memory)s</memory>
  <currentMemory unit='KiB'>%(memory)s</currentMemory>
  <vcpu placement='static'>%(vcpu)s</vcpu>
  <os>
    <type arch='%(march)s' machine='pc-i440fx-2.0'>hvm</type>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
  </features>
  <clock offset='utc'>
    <timer name='rtc' tickpolicy='catchup'/>
    <timer name='pit' tickpolicy='delay'/>
    <timer name='hpet' present='no'/>
  </clock>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <pm>
    <suspend-to-mem enabled='no'/>
    <suspend-to-disk enabled='no'/>
  </pm>
  <devices>
    <emulator>/usr/bin/qemu-system-%(arch)s</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='%(path)s'/>
      <target dev='vda' bus='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
    </disk>
    <controller type='usb' index='0' model='ich9-ehci1'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x7'/>
    </controller>
    <controller type='usb' index='0' model='ich9-uhci1'>
      <master startport='0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0' multifunction='on'/>
    </controller>
    <controller type='usb' index='0' model='ich9-uhci2'>
      <master startport='2'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x1'/>
    </controller>
    <controller type='usb' index='0' model='ich9-uhci3'>
      <master startport='4'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x2'/>
    </controller>
    <controller type='pci' index='0' model='pci-root'/>
    <controller type='virtio-serial' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
    </controller>
    %(network)s
    <serial type='pty'>
      <target port='0'/>
    </serial>
    <console type='pty'>
      <target type='serial' port='0'/>
    </console>
    <channel type='spicevmc'>
      <target type='virtio' name='com.redhat.spice.0'/>
      <address type='virtio-serial' controller='0' bus='0' port='1'/>
    </channel>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    <graphics type='spice' autoport='no' port="%(spice_port)s" listen='%(spice_ip)s'>
      <listen type='address' address='%(spice_ip)s'/>
      <image compression='off'/>
    </graphics>
    <sound model='ich6'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </sound>
    <video>
      <model type='qxl' ram='65536' vram='65536' vgamem='16384' heads='1'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <redirdev bus='usb' type='spicevmc'>
    </redirdev>
    <redirdev bus='usb' type='spicevmc'>
    </redirdev>
    <memballoon model='virtio'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x08' function='0x0'/>
    </memballoon>
  </devices>
</domain>
"""


INTERFACE = """"<interface type='bridge'>
      <mac address='%(address)s'/>
      <source bridge='%(bridge)s'/>
      <virtualport type='openvswitch'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='%(slot)s' function='0x0'/>
    </interface>"""


try:
    from StringIO import StringIO as io
except:
    from io import StringIO as io


class Host(object):
    conn = None

    def get_arch(self):
        if self.instance.architecture == 'i386':
            return ('i386', 'i686')
        return (self.instance.architecture, self.instance.architecture)

    def get_image_path(self):
        newpath = self.instance.image.path.replace(".img", '')

        instance_path = newpath + "_%d.img" % (self.instance.pk,)
        if not os.path.exists(instance_path):
            cmd = "sudo cp %s %s" % (
                self.instance.image.path,
                instance_path
            )
            self.bash.execute(cmd)
        return instance_path

    def get_connection(self):
        if not self.conn:
            SASL_USER = 'usuario'
            SASL_PASS = 'enrique'

            def request_cred(credentials, user_data):
                for credential in credentials:
                    if credential[0] == libvirt.VIR_CRED_AUTHNAME:
                        credential[4] = SASL_USER
                    elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
                        credential[4] = SASL_PASS
                return 0
            auth = [
                [libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE], request_cred, None]

            self.conn = libvirt.openAuth(
                'qemu+tcp://localhost/system', auth, 0)
            #self.conn = libvirt.open("qemu:///system")
        return self.conn

    def create_domain(self):
        conn = self.get_connection()
        self.name = self.instance.bridge.name + "_" + str(self.instance.pk)
        arch, march = self.get_arch()
        data = {
            'name': self.name,
            'uuid': self.instance.uuid,
            'memory': self.instance.memory,
            'vcpu': self.instance.vcpu,
            'arch': arch,
            'march': march,
            'path': self.get_image_path(),
            'network': self.get_network_interface(),
            'spice_port': str(5000 + self.instance.pk),
            'spice_ip': "0.0.0.0"

        }
        xml = BASE_XML % data
        conn.defineXML(xml)

    def create_host(self):
        self.create_domain()
        vm = self.conn.lookupByName(self.name)
        vm.create()

    def delete_host(self):
        conn = self.get_connection()
        self.name = self.instance.bridge.name + "_" + str(self.instance.pk)
        vm = conn.lookupByName(self.name)
        vm.destroy()
        vm.undefine()

    def get_network_interface(self):
        dev = ""
        naturalname = get_natural_name(self.instance)
        links = Link.objects.filter(
            Q(to_obj=self.instance.pk,
              to_naturalname=naturalname
              ) | Q(
                from_obj=self.instance.pk,
                from_naturalname=naturalname
            )
        )
        slot = 10
        for link in links:
            dev += INTERFACE % {
                "address": self.get_mac_address(link),
                "bridge": self.instance.bridge.get_name(),
                "slot": "0x%d" % (slot,)
            }
        return dev

    def get_mac_address(self, link):
        if link.mac:
            return link.mac

        return get_random_mac()

    def __init__(self, instance, shell):
        self.bash = shell
        self.instance = instance
