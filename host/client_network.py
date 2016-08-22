#!/usr/bin/python

import netifaces
import requests
import subprocess
import logging
from datetime import datetime
import time
import socket

SLEEP_TIME = 25  # seconds
BASH_CREATE_TUNNEL = """
ip link add %(iface)s type gretap local %(ip_local)s remote %(ip_remote)s key %(key)s;
ip link set %(iface)s up multicast on mtu 1420
"""
BASH_SET_IP = """ifconfig %(iface)s %(addr)s  netmask %(netmask)s broadcast %(broadcast)s"""
BASH_DEL_TUNNEL = "ip link del %s; "
BASH_ADD_ROUTE = "ip route add %s dev %s; "
BASH_ADD_ROUTE_VIA = "ip route add %(net)s via %(via)s dev %(dev)s; "
BASH_SET_ROUTE_VIA = "ip link set dev %(dev)s up; ip route add %(net)s/%(mask)s dev %(dev)s; ip route add %(net)s via %(via)s dev %(dev)s; "
LIST_INTERFACES = "ls /sys/class/net"
BASH_LIST_ROUTE = "ip route list"
BASH_DEL_ROUTE = "ip route del %s; "
BASH_DHCP_CLIENT = "dhclient %s"


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

    def get_ip_base_interface(self):
        base_name = self.get_base_interface()
        info = netifaces.ifaddresses(base_name)
        return info[netifaces.AF_INET][0]['addr']

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
            dhcp = ['eth0', 'host0' ]
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

        if 'dhcp' in data:
            self.call_dhcp(data['dhcp'])

    def call_dhcp(self, ifaces):
        for iface in ifaces:
            self._bash.execute(BASH_DHCP_CLIENT % iface)

    def set_routes(self, route_list):
        routes = ""
        devs = {}
        for route in route_list:
            if route['dev'] not in devs:
                devs[route['dev']] = 0
            if 'via' in route:
                if devs[route['dev']] == 0:
                    net_tmp = route['net'].split("/")
                    net, mask = net_tmp[0], net_tmp[
                        1] if len(net_tmp) > 1 else "32"
                    routes += BASH_SET_ROUTE_VIA % {
                        'dev': route['dev'],
                        'net': net,
                        'mask': mask,
                        'via': route['via']
                    }
                    devs[route['dev']] += 1
                else:
                    routes += BASH_ADD_ROUTE_VIA % route
                    devs[route['dev']] += 1

            else:
                routes += BASH_ADD_ROUTE % (
                    route['net'],
                    route['dev']
                )

        self._bash.execute(routes)

    def remove_gateways(self):
        # gws = netifaces.gateways()  # Sorry not working
        output = self._bash.execute(BASH_LIST_ROUTE)
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
            exec_cmd += BASH_DEL_ROUTE % route
        self._bash.execute(exec_cmd)


class Server:
    port = 9798
    server_address = None
    sock = None

    def __init__(self, host):
        self._host = host

    def get_socket_bind_address(self):
        ip_addr = self._host.get_ip_base_interface()
        return (ip_addr, self.port)

    def connect(self):
        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.server_address)
        self.sock.listen(1)

    def disconnect(self):
        self.sock.setblocking(False)
        self.sock.close()

    def listen(self):
        self.server_address = self.get_socket_bind_address()

        logging.info("Listen %s:%d" % self.server_address)
        finish = False
        self.connect()
        while not finish:
            connection, client_address = self.sock.accept()
            try:
                data = connection.recv(2)
                value = int(data)
                if value == 1:
                    finish = True
            except:
                pass
            finally:
                connection.close()
        self.disconnect()
        self.reload()

    def reload(self):
        self._host.delete_tunnels()
        self._host.get_ips_from_control()
        self.listen()

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
    server = Server(host)
    server.listen()
