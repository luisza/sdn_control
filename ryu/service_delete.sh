#!/bin/bash


if [ -a /etc/systemd/system/ryu_$1.service  ]; then
    systemctl disable ryu_$1.service
    service ryu_$1 stop
    rm /etc/systemd/system/ryu_$1.service
    systemctl daemon-reload
fi
