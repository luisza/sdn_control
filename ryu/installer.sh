#!/bin/bash

# ./installer.sh apps/simple_switch_13.py
#
#  iptables -A INPUT -p tcp -m tcp --dport 6633 -j ACCEPT
mkdir -p /etc/ryuctrl/
rm -rf /etc/ryuctrl/apps
cp -a apps /etc/ryuctrl/

rm /etc/systemd/system/ryu.service
cp ryu.service.default /etc/systemd/system/ryu.service
chmod 664 /etc/systemd/system/ryu.service

ryu_service=$1

sed -i "s/APPS/\/etc\/ryuctrl\/apps\/"$ryu_service"/g" /etc/systemd/system/ryu.service



systemctl daemon-reload
systemctl enable ryu.service
service ryu restart
