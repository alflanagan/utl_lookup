# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0011_require_packagedep_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utlfile',
            name='file',
            field=models.FileField(blank=True, upload_to='utl_files', null=True),
        ),
    ]
