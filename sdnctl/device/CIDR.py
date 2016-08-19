# encoding: utf-8

'''
Free as freedom will be 19/8/2016

thanks http://terminalmage.net/2012/06/10/how-to-find-out-the-cidr-notation-for-a-subnet-given-an-ip-and-netmask.html

@author: luisza
'''

from __future__ import unicode_literals


def get_net_size(netmask):
    binary_str = ''
    for octet in netmask:
        binary_str += bin(int(octet))[2:].zfill(8)
    return str(len(binary_str.rstrip('0')))
