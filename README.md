# sdn_control
Network overlay web controller and host client

###  :warning: this software is in development and is not stable jet so is not for production environment

## What I can do with this software?

You can create an overlay network based on tunnels gre (greptap) and OpenVswitch.
So you can create sdn networks over common networks without any special 
configuration on physical network device or network.

## Requirements and Installation

This software has 2 sections *host* and *server*, that has diferents requirements

#### Host

See host/requirements.txt for python requirements. The System requirements are
systemd and ip2 that are common sofware in rpm and deb based distros.

You also need a network interface with ip-address that can comunicate with server client.

Simplest way to install this software is using de installer *host/installer.sh*
so run as root

```
# cd host/
# bash installer.sh
```
you can change some configurations in 

`/etc/sdnnetclient/sdnnetclient.conf`

:warning: Before running host please configure the server client

#### Host

This control panel is django based software.

This software use ssh client to connect openvswitch machine and configure then 
lauching shell command son openssh server and bash are requirements also ip2 and
network-tools (ifconfig).

See requirement.txt for python requirements. run
 
`sudo pip install -r requirements.txt`

Install and configure openvswitch in one or more machines (:confused: sorry out of scope)

Install and configure openssh server in all machines with openvswitch and configure 
login with rsa key howto [here](http://www.linuxproblem.org/art_9.html). 

You also need to set in sdn_control/settings.py the ssh login user

`SSH_USER = "your ssh login user"`

this user also need to do a sudo commands without password for specific programs
so edit */etc/sudoers* and add at the end this

```
myuser ALL = (root) NOPASSWD: /usr/bin/ovs-vsctl
myuser ALL = (root) NOPASSWD: /usr/sbin/ip
Defaults:myuser !requiretty
```




