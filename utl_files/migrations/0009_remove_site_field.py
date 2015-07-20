# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0008_rename_model'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='package',
            unique_together=set([('name', 'version')]),
        ),
        migrations.RemoveField(
            model_name='package',
            name='site',
        ),
    ]
