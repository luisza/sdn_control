# encoding: utf-8


'''
Created on 4/12/2016

@author: luisza
'''
from __future__ import unicode_literals
from sdnctl.bash_commands import BASH_CREATE_CONTROLLER, BASH_DELETE_CONTROLLER


class RyuController(object):

    def start(self):

        cmd = BASH_CREATE_CONTROLLER % {
            'port': self.instance.port,
            'apps': self.instance.get_apps(),
            'ip': self.instance.ip,
            'wshost': self.instance.wsapi_host,
            'wsport': self.instance.wsapi_port
        }
        self._bash.execute(cmd)

    def stop(self):
        cmd = BASH_DELETE_CONTROLLER % {
            'port': str(self.instance.port)
        }
        self._bash.execute(cmd)

    def __init__(self, instance, bash):
        self.instance = instance
        self._bash = bash
