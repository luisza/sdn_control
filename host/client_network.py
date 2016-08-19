#!/usr/bin/python

import netifaces
import requests
import subprocess
import logging
from datetime import datetime
import time

SLEEP_TIME = 25  # seconds
BASH_CREATE_TUNNEL = """
ip link add %(iface)s type gretap local %(ip_local)s remote %(ip_remote)s key %(key)s;
ip link set %(iface)s up multicast on mtu 1420
"""
BASH_SET_IP = """ifconfig %(iface)s %(addr)s  netmask %(netmask)s broadcast %(broadcast)s"""
BASH_SET_ROUTES = "%s"
BASH_DEL_TUNNEL = "ip link del %s"

BASH_SET_ROUTE_VIA = "ip link set dev %(dev)s up; ip route add %(net)s/%(mask)s dev %(dev)s; ip route add %(net)s via %(via)s dev %(dev)s; "
LIST_INTERFACES = "ls /sys/class/net"


class Bash:

    def __init__(self, log_file="log_client_network.log"):
        logging.basicConfig(filename=log_file, level=logging.INFO)
        logging.info('\nStarted at %s', datetime.now().isoformat())

    def execute(self, str_command):
        logging.info("BASH:\t\t" + str_command.replace(";", ";\n"))
        output = subprocess.check_output(['bash', '-c', str_command])
        return output


class Host:
    control_url = None

    _base_interface = None
    _mac_addr = None
    _bash = None

    def __init__(self, control_url="http://127.0.0.1",
                 log_file="log_client_network.log"):
        self.control_url = control_url
        self._bash = Bash(log_file=log_file)

    def get_base_interface(self):
        if self._base_interface is None:
            interfaces = [
                x for x in netifaces.interfaces() if "lo" not in x and "host" not in x]
            self._base_interface = interfaces[0]
        return self._base_interface

    def get_host_interface(self):
        # return  [x for x in netifaces.interfaces() if "host" in x ]
        output = self._bash.execute(LIST_INTERFACES)
        return [x for x in output.split("\n") if "host" in x]

    def get_mac_address(self):
        if self._mac_addr is not None:
            return self._mac_addr

        mac_addr = "ff:ff:ff:ff:ff"
        info_dev = netifaces.ifaddresses(self.get_base_interface())
        if netifaces.AF_LINK in info_dev:
            mac_addr = info_dev[netifaces.AF_LINK][0]['addr']
            self._mac_addr = mac_addr
        return mac_addr

    def config_interface(self, iface, addr, netmask, broadcast):
        self._bash.execute(BASH_SET_IP % {
            'iface': iface, 'addr': addr,
            'netmask': netmask, 'broadcast': broadcast
        })

    def delete_tunnels(self):
        exec_cmd = ""

        for iface in self.get_host_interface():
            exec_cmd += BASH_DEL_TUNNEL % (iface)
        self._bash.execute(exec_cmd)

    def create_tunnel(self, iface, ip_local, ip_remote, key):
        self._bash.execute(BASH_CREATE_TUNNEL % {
            'iface': iface, 'key': key,
            'ip_local': ip_local, 'ip_remote': ip_remote
        })

    def get_ips_from_control(self):
        params = {'mac': self.get_mac_address()}
        assigned_ip = False
        # Fixme: Infinite loop posibility
        while not assigned_ip:
            try:
                r = requests.get(self.control_url, params=params)
                assigned_ip = r.status_code == 200
            except:
                time.sleep(SLEEP_TIME)

        """{
            dev_iface = [{iface: 'eth0', addr: '',
						netmask: '', broadcast: '' }]
            dev_tunnel = [
                    { iface: 'host0', ip_local: '' 
                      ip_remote: '' key:'' }
                         ]
            route = [
                { net: 'default', dev: 'eth0'}
                { net: '' via: '' dev: '' }
                    ]
            }
        """

        data = r.json()

        for tunnel in data['dev_tunnel']:
            self.create_tunnel(tunnel['iface'], tunnel['ip_local'],
                               tunnel['ip_remote'], tunnel['key'])

        for dev_iface in data['dev_iface']:
            self.config_interface(dev_iface['iface'],
                                  dev_iface['addr'],
                                  dev_iface['netmask'],
                                  dev_iface['broadcast'])

        self.remove_gateways()
        self.set_routes(data['route'])

    def set_routes(self, route_list):
        routes = ""
        for route in route_list:
            if 'via' in route:
                net_tmp = route['net'].split("/")
                net, mask = net_tmp[0], net_tmp[
                    1] if len(net_tmp) > 1 else "32"
                routes += BASH_SET_ROUTE_VIA % {
                    'dev': route['dev'],
                    'net': net,
                    'mask': mask,
                    'via': route['via']
                }

            else:
                routes += "ip route add %s dev %s; " % (
                    route['net'],
                    route['dev']
                )

        self._bash.execute(BASH_SET_ROUTES % (routes,))

    def remove_gateways(self):
        # gws = netifaces.gateways()  # Sorry not working
        output = self._bash.execute("ip route list")
        routes = []
        for line in output.split("\n"):
            if not line:
                continue
            route = line.split(" ")
            if 'via' == route[1]:
                route = " ".join(route)
            else:
                route = " ".join(route[:3])
            routes.append(route)

        exec_cmd = ""
        for route in routes:
            exec_cmd += "ip route del %s; " % route
        self._bash.execute(exec_cmd)


if __name__ == '__main__':
    import ConfigParser
    config = ConfigParser.ConfigParser()
    if config.read("/etc/sdnnetclient/sdnnetclient.conf"):
        pass
    else:
        config.read("sdnnetclient.conf")

    host = Host(control_url=config.get('basic', 'control_url'),
                log_file=config.get('basic', 'log_file')
                )
    host.delete_tunnels()
    host.get_ips_from_control()
