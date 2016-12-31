#!/bin/bash

apt-get install libmysqlclient-dev

CREATE DATABASE sdnctl;
GRANT ALL ON sdnctl.* TO 'sdnctl'@'%' IDENTIFIED BY '$#sasaerES873';

echo "192.168.155.2   sdnctl.db sdnctl.db" >> /etc/hosts


en /etc/mysql/my.cnf
[mysqld]
skip-name-resolve
