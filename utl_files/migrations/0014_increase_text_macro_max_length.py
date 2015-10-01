# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0013_increase_path_max_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='macroref',
            name='macro_name',
            field=models.CharField(help_text='The ID or expression identifying the macro to be called.', max_length=500),
        ),
        migrations.AlterField(
            model_name='macroref',
            name='text',
            field=models.CharField(help_text='The actual text of the macro call, with args.', max_length=1000),
        ),
    ]
