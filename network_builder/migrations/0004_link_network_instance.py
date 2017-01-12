# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-04 19:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network_builder', '0003_auto_20170104_1927'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='network_instance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='network_builder.NetworkBuild'),
        ),
    ]
