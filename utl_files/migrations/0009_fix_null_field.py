# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-13 22:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0008_add_used_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='app',
            field=models.ForeignKey(blank=True, help_text='The application to which this package belongs', null=True, on_delete=django.db.models.deletion.CASCADE, to='utl_files.Application'),
        ),
    ]
