# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-04 22:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0005_allow_blank_on_null_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='utlfile',
            name='file',
        ),
        migrations.RemoveField(
            model_name='utlfile',
            name='pkg_directory',
        ),
    ]
