# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0014_increase_text_macro_max_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='macroref',
            name='macro_name',
            field=models.CharField(max_length=4000, help_text='The ID or expression identifying the macro to be called.'),
        ),
        migrations.AlterField(
            model_name='macroref',
            name='text',
            field=models.CharField(max_length=4000, help_text='The actual text of the macro call, with args.'),
        ),
        migrations.AlterUniqueTogether(
            name='macroref',
            unique_together=set([('source', 'start', 'macro_name')]),
        ),
    ]
