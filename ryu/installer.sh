#!/bin/bash

# ./installer.sh apps/simple_switch_13.py
#
#  iptables -A INPUT -p tcp -m tcp --dport 6633 -j ACCEPT

echo "Remember: First install ryu controller with pip install ryu"
mkdir -p /etc/ryuctrl/
cp ryu.service.default /etc/ryuctrl/
cp service_creator.sh /etc/ryuctrl/service_creator.sh
cp service_delete.sh /etc/ryuctrl/service_delete.sh
chmod +x /etc/ryuctrl/service_creator.sh
chmod +x /etc/ryuctrl/service_delete.sh


RYU=$(which ryu-manager)
RYU=${RYU//\//\\\/}
sed -i "s/RYU/$RYU/g" /etc/ryuctrl/ryu.service.default

python setup.py sdist
pip install -U dist/sdnctlryuapps-0.0.1.tar.gz
