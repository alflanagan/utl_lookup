# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0004_order_vnames'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='site',
            field=models.ForeignKey(to='papers.TNSite'),
        ),
        migrations.DeleteModel(
            name='TNSite',
        ),
    ]
