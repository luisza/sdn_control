# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-02 05:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network_builder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='router',
            name='default_gateway',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='architecture',
            field=models.CharField(choices=[('x86_64', 'x86_64'), ('i386', 'x86')], default='x86_64', max_length=25),
        ),
        migrations.AlterField(
            model_name='machineimage',
            name='name',
            field=models.CharField(blank=True, default='Cirros x86_64', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='machineimage',
            name='path',
            field=models.CharField(blank=True, default='/var/lib/libvirt/images/cirros-0.3.4-x86_64-disk.img', max_length=250, null=True),
        ),
    ]
