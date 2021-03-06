# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-22 02:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sdnctl', '0006_dhcp_server_dhcp_static_ip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dhcp_server',
            name='lease_time',
            field=models.CharField(default='infinite', max_length=10),
        ),
        migrations.AlterField(
            model_name='dhcp_static_ip',
            name='lease_time',
            field=models.CharField(default='infinite', help_text='03m/infinite/ignore', max_length=10),
        ),
    ]
