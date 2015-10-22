# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0007_fix_verbose_names'),
    ]

    operations = [
        migrations.CreateModel(
            name='PackageProp',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('key', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=250)),
                ('pkg', models.ForeignKey(to='utl_files.Package', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'package properties',
                'verbose_name': 'package property',
            },
        ),
        migrations.AlterUniqueTogether(
            name='packageprops',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='packageprops',
            name='pkg',
        ),
        migrations.DeleteModel(
            name='PackageProps',
        ),
        migrations.AlterUniqueTogether(
            name='packageprop',
            unique_together=set([('pkg', 'key')]),
        ),
    ]
