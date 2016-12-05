#!/bin/bash
#
#  iptables -A INPUT -p tcp -m tcp --dport 6633 -j ACCEPT


WSAPI=" --wsapi-host $4 --wsapi-port $5"



cp /etc/ryuctrl/ryu.service.default /etc/systemd/system/ryu_$1.service
chmod 664 /etc/systemd/system/ryu_$1.service

APPS=${3//\//\\\/}

sed -i "s/IP/$2/g" /etc/systemd/system/ryu_$1.service
sed -i "s/PORT/$1/g" /etc/systemd/system/ryu_$1.service
sed -i "s/APPS/$APPS/g" /etc/systemd/system/ryu_$1.service
sed -i "s/EXTRAS/$WSAPI/g" /etc/systemd/system/ryu_$1.service

iptables -A INPUT -p tcp -m tcp --dport $1 -j ACCEPT

systemctl daemon-reload
systemctl enable ryu_$1.service
service ryu_$1 restart
