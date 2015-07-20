# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0006_add_pkgdeps_pkgprops'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='packagedep',
            options={'verbose_name': 'package dependency', 'verbose_name_plural': 'package dependencies'},
        ),
        migrations.AlterModelOptions(
            name='packageprops',
            options={'verbose_name': 'package property', 'verbose_name_plural': 'package properties'},
        ),
    ]
