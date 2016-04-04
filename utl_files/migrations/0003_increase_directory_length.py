# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-23 19:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0002_allow_null_last_download'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='disk_directory',
            field=models.FilePathField(allow_files=False, allow_folders=True, blank=True, help_text="The location of the package's files on disk, relative to some common root directory.", max_length=4096),
        ),
    ]