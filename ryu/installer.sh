#!/bin/bash

# ./installer.sh apps/simple_switch_13.py

mkdir -p /etc/ryuctrl/
cp -a apps /etc/ryuctrl/

cp ryu.service.default /etc/systemd/system/ryu.service
chmod 664 /etc/systemd/system/ryu.service

ryu_service=$1

sed -i "s/APPS/\/etc\/ryuctrl\/"$ryu_service"/g" /etc/systemd/system/ryu.service

systemctl daemon-reload
systemctl enable ryu.service
service ryu restart
