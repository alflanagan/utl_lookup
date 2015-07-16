# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0002_auto_20150622_1701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tnsite',
            name='name',
            field=models.CharField(max_length=100, blank=True),
        ),
    ]
