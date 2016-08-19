# encoding: utf-8

'''
Free as freedom will be 15/8/2016

@author: luisza
'''

from __future__ import unicode_literals
import spur
import logging


class SSHConnection(object):

    def __init__(self, host, port=22,
                 user="root",
                 key_path='rsa_key.pem',
                 log_file="sdnctl_server_log.log"):
        self.host = host
        self.port = port
        self.key_path = key_path
        self.user = user
        self.shell = None
        logging.basicConfig(filename=log_file, level=logging.INFO)

    def connect(self):
        logging.info("BASH:\t\tConnecting with %s@%s" % (self.user,
                                                         self.host))
        self.shell = spur.SshShell(
            hostname=self.host,
            username=self.user,
            private_key_file=self.key_path,
            missing_host_key=spur.ssh.MissingHostKey.warn
        )

    def execute(self, str_command, allow_error=False):
        if not self.shell:
            self.connect()
        logging.info("BASH:(%s@%s)\t\t%s" % (
            self.user,
            self.host,
            str_command.replace(";", ";\n")))
        result = self.shell.run(
            ['bash', '-c', str_command], allow_error=allow_error)
        return result

    def close(self):
        self.shell = None
