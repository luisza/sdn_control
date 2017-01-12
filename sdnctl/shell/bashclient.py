# encoding: utf-8


'''
Created on 9/12/2016

@author: luisza
'''
from __future__ import unicode_literals
import logging
import subprocess


class BashClient:

    def __init__(self, host="localhost", port=22,
                 user=None,
                 key_path='rsa_key.pem',
                 log_file="sdnctl_server_log.log"):

        logging.basicConfig(filename=log_file, level=logging.INFO)

    def connect(self):
        pass

    def execute(self, str_command, allow_error=False):
        print(str_command)
        dev = ''
        if allow_error:
            try:
                dev = subprocess.check_output(str_command, shell=True)
            except:
                pass
        else:
            dev = subprocess.check_output(str_command, shell=True)
        return dev

    def close(self):
        pass
