# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-15 02:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import sdnctl.model_logic


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac', models.CharField(max_length=100)),
            ],
            bases=(models.Model, sdnctl.model_logic.HostLogic),
        ),
        migrations.CreateModel(
            name='NetworkBridge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('base_ip', models.GenericIPAddressField()),
                ('netmask', models.CharField(max_length=33)),
                ('broadcast', models.GenericIPAddressField()),
            ],
        ),
        migrations.CreateModel(
            name='NIC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interface', models.CharField(max_length=10)),
                ('address', models.GenericIPAddressField(blank=True, null=True)),
                ('netmask', models.CharField(blank=True, max_length=33, null=True)),
                ('broadcast', models.GenericIPAddressField(blank=True, null=True)),
                ('default_gw', models.BooleanField(default=False)),
                ('is_control', models.BooleanField(default=False)),
            ],
            bases=(models.Model, sdnctl.model_logic.NICLogic),
        ),
        migrations.CreateModel(
            name='OVS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('control_ip', models.GenericIPAddressField()),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('network', models.GenericIPAddressField()),
                ('netmask', models.CharField(default='/24', help_text='abrev mode ej. /24', max_length=3)),
                ('via', models.GenericIPAddressField(blank=True, null=True)),
            ],
            bases=(models.Model, sdnctl.model_logic.RouteLogic),
        ),
        migrations.CreateModel(
            name='Logical_NIC',
            fields=[
                ('nic_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='sdnctl.NIC')),
                ('is_dhcp', models.BooleanField(default=False)),
                ('key', models.SmallIntegerField(default=1)),
            ],
            bases=('sdnctl.nic',),
        ),
        migrations.AddField(
            model_name='nic',
            name='host',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sdnctl.Host'),
        ),
        migrations.AddField(
            model_name='nic',
            name='routes',
            field=models.ManyToManyField(to='sdnctl.Route'),
        ),
        migrations.AddField(
            model_name='networkbridge',
            name='ovs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sdnctl.OVS'),
        ),
        migrations.AddField(
            model_name='logical_nic',
            name='bridge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sdnctl.NetworkBridge'),
        ),
    ]
