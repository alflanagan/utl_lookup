# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0012_utlfile_file_null_blank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utlfile',
            name='file_path',
            field=models.FilePathField(help_text='The file path, relative to the package base directory.', max_length=1024),
        ),
    ]
