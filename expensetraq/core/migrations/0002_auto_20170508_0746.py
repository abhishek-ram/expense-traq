# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-08 07:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salesman',
            old_name='region',
            new_name='regions',
        ),
    ]