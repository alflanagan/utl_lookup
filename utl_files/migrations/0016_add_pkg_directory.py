# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0015_expand_and_fix_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='utlfile',
            name='pkg_directory',
            field=models.CharField(default='', max_length=1024, help_text='The package base directory on the hard drive.'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='utlfile',
            name='file_path',
            field=models.FilePathField(max_length=2048, help_text='The file path, relative to the package base directory.'),
        ),
    ]
