# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='name',
            field=models.CharField(unique=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='tnsite',
            name='URL',
            field=models.URLField(unique=True, max_length=250),
        ),
        migrations.AlterUniqueTogether(
            name='package',
            unique_together=set([('name', 'version', 'site', 'app')]),
        ),
        migrations.AlterUniqueTogether(
            name='utlfile',
            unique_together=set([('pkg', 'file_path')]),
        ),
    ]
