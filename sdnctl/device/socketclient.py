# encoding: utf-8

'''
Free as freedom will be 20/8/2016

@author: luisza
'''

from __future__ import unicode_literals
import logging
import socket


class SocketClient:
    port = 9798

    def __init__(self, ip_addr,
                 log_file="sdnctl_server_log.log"):
        self.ip_addr = ip_addr
        self.socket = None
        self.server_address = (self.ip_addr, self.port)

        logging.basicConfig(filename=log_file, level=logging.INFO)

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.server_address)

    def close(self):
        self.socket.close()
        self.socket = None

    def execute(self, msg="1"):
        if not self.socket:
            self.connect()
        self.socket.sendall(msg)
        self.close()
