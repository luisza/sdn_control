#!/bin/sh

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi


if [ -f /etc/debian_version ]; then
    echo "This is debian based distro"
	apt-get install -y python-netifaces python-requests 
elif [ -f /etc/redhat-release ]; then
    echo "This is RedHat based distro"
	yum install python-netifaces python-requests 
else
    echo "Sorry not debian or redhat based distro"
	exit 1
fi

bin_python=$(whereis  -b python | awk '{print $2}')
bin_python_sed="${bin_python//\//\\/}"
cp client_network.py /usr/bin/client_network.py
chmod +x /usr/bin/client_network.py

mkdir -p /etc/sdnnetclient/
cp sdnnetclient.conf /etc/sdnnetclient/sdnnetclient.conf

cp sdnnetclient.service /etc/systemd/system/sdnnetclient.service
chmod 664 /etc/systemd/system/sdnnetclient.service
sed -i "s/python/"$bin_python_sed"/g" /etc/systemd/system/sdnnetclient.service

mkdir -p /var/lib/sdnnetclient/
touch /var/lib/sdnnetclient/sdnnetclient.pid


systemctl daemon-reload
systemctl enable sdnnetclient
echo "Service sdnnetclient enabled"
echo "Service isn't started by default use systemctl start sdnnetclient"

iptables -A INPUT -p tcp -m tcp --dport 9798 -j ACCEPT
