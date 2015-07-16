# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0003_tnsite_name_blank'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='application',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='tnsite',
            options={'verbose_name': 'Townnews Site'},
        ),
        migrations.AlterModelOptions(
            name='utlfile',
            options={'verbose_name': 'UTL File'},
        ),
    ]
