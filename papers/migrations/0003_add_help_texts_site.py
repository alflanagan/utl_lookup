# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-01 18:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('papers', '0002_townnewssite_initial_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='townnewssite',
            name='URL',
            field=models.URLField(help_text='The sites main URL', max_length=250, unique=True),
        ),
        migrations.AlterField(
            model_name='townnewssite',
            name='name',
            field=models.CharField(blank=True, help_text='The site brand (may be same as URL)', max_length=100),
        ),
    ]
