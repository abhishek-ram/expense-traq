# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-09 04:46
from __future__ import unicode_literals

from django.db import migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20170508_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expensetypecode',
            name='region',
            field=localflavor.us.models.USStateField(max_length=2),
        ),
    ]
