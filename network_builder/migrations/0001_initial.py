# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-30 22:49
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sdnctl', '0014_auto_20161209_1918'),
    ]

    operations = [
        migrations.CreateModel(
            name='BridgeLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='DHCP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_ip', models.GenericIPAddressField()),
                ('end_ip', models.GenericIPAddressField()),
                ('lease_time', models.CharField(default='infinite', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='DHCP_Static_IP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac', models.CharField(max_length=100)),
                ('address', models.GenericIPAddressField()),
                ('hostname', models.CharField(blank=True, max_length=33, null=True)),
                ('lease_time', models.CharField(default='infinite', help_text='03m/infinite/ignore', max_length=10)),
                ('dhcp_server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network_builder.DHCP')),
            ],
        ),
        migrations.CreateModel(
            name='Firewall',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='Firewall', max_length=250, null=True)),
                ('switch_id', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FirewallRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(65535)])),
                ('dl_src', models.CharField(blank=True, help_text='xx:xx:xx:xx:xx:xx', max_length=50, null=True, verbose_name='Source MAC')),
                ('dl_dst', models.CharField(blank=True, help_text='xx:xx:xx:xx:xx:xx', max_length=50, null=True, verbose_name='Destination MAC')),
                ('dl_type', models.CharField(choices=[('ARP', 'ARP'), ('Ipv4', 'Ipv4')], default='Ipv4', max_length=5)),
                ('nw_src', models.CharField(blank=True, help_text='xxx.xxx.xxx.xxx/xx', max_length=50, null=True, verbose_name='Source Address')),
                ('nw_dst', models.CharField(blank=True, help_text='xxx.xxx.xxx.xxx/xx', max_length=50, null=True, verbose_name='Destination Address')),
                ('nw_proto', models.CharField(blank=True, choices=[('TCP', 'TCP'), ('UDP', 'UDP'), ('ICMP', 'ICMP'), ('ICMPv6', 'ICMPv6')], max_length=7, null=True, verbose_name='Protocol')),
                ('tp_src', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(65535)], verbose_name='Source Port')),
                ('tp_dst', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(65535)], verbose_name='Destination Port')),
                ('actions', models.CharField(choices=[('ALLOW', 'ALLOW'), ('DENY', 'DENY')], max_length=6)),
                ('firewall', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network_builder.Firewall')),
            ],
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='Host', max_length=250, null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('memory', models.IntegerField(default=256000)),
                ('vcpu', models.SmallIntegerField(default=1)),
                ('architecture', models.CharField(choices=[('x86', 'x86'), ('x86_64', 'x86_64')], default='x86', max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_dhcp', models.BooleanField(default=True)),
                ('mac', models.CharField(blank=True, help_text='xx:xx:xx:xx:xx:xx', max_length=50, null=True, verbose_name='Source MAC')),
                ('address', models.GenericIPAddressField(blank=True, null=True)),
                ('netmask', models.CharField(blank=True, default='255.255.255.0', max_length=33, null=True)),
                ('broadcast', models.GenericIPAddressField(blank=True, null=True)),
                ('speed', models.IntegerField(default=100, help_text='MB')),
                ('from_obj', models.IntegerField(default=0)),
                ('from_naturalname', models.CharField(default='network_builder.Router', max_length=250)),
                ('to_obj', models.IntegerField(default=0)),
                ('to_naturalname', models.CharField(default='network_builder.Host', max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='MachineImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='Cirros x86', max_length=250, null=True)),
                ('path', models.CharField(blank=True, default='/var/lib/libvirt/images/cirros-0.3.4-i386-disk.img', max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('network', models.CharField(max_length=250)),
                ('gateway', models.GenericIPAddressField()),
            ],
        ),
        migrations.CreateModel(
            name='NetworkBridge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='br0', max_length=250)),
                ('controller', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sdnctl.SDNController')),
            ],
        ),
        migrations.CreateModel(
            name='NetworkBuild',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='mynetwork', max_length=250)),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Router',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='router', max_length=250, null=True)),
                ('switch_id', models.CharField(blank=True, max_length=20, null=True)),
                ('bridge', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='network_builder.NetworkBridge')),
                ('network_instance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='network_builder.NetworkBuild')),
            ],
        ),
        migrations.CreateModel(
            name='RouterAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, help_text='127.0.0.1/24', max_length=250, null=True)),
                ('router', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network_builder.Router')),
            ],
        ),
        migrations.AddField(
            model_name='networkbridge',
            name='network_instance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='network_builder.NetworkBuild'),
        ),
        migrations.AddField(
            model_name='networkbridge',
            name='ovs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sdnctl.OVS'),
        ),
        migrations.AddField(
            model_name='network',
            name='router',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network_builder.Router'),
        ),
        migrations.AddField(
            model_name='host',
            name='bridge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='network_builder.NetworkBridge'),
        ),
        migrations.AddField(
            model_name='host',
            name='image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='network_builder.MachineImage'),
        ),
        migrations.AddField(
            model_name='host',
            name='network_instance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='network_builder.NetworkBuild'),
        ),
        migrations.AddField(
            model_name='firewall',
            name='bridge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='network_builder.NetworkBridge'),
        ),
        migrations.AddField(
            model_name='firewall',
            name='network_instance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='network_builder.NetworkBuild'),
        ),
        migrations.AddField(
            model_name='dhcp',
            name='bridge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='network_builder.NetworkBridge'),
        ),
        migrations.AddField(
            model_name='dhcp',
            name='network_instance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='network_builder.NetworkBuild'),
        ),
        migrations.AddField(
            model_name='bridgelink',
            name='base',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='base', to='network_builder.NetworkBridge'),
        ),
        migrations.AddField(
            model_name='bridgelink',
            name='network_instance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='network_builder.NetworkBuild'),
        ),
        migrations.AddField(
            model_name='bridgelink',
            name='related_bridges',
            field=models.ManyToManyField(related_name='related_bridges', to='network_builder.NetworkBridge'),
        ),
    ]
