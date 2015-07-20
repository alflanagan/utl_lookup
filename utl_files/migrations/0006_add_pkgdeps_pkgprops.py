# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0005_remove_tnsite'),
    ]

    operations = [
        migrations.CreateModel(
            name='PackageDep',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('dep_name', models.CharField(max_length=200)),
                ('dep_version', models.CharField(max_length=50)),
                ('dep_pkg', models.ForeignKey(related_name='dep_pkg', to='utl_files.Package', null=True)),
                ('pkg', models.ForeignKey(to='utl_files.Package')),
            ],
            options={
                'verbose_name': 'Package Dependency',
            },
        ),
        migrations.CreateModel(
            name='PackageProps',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('key', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=250)),
                ('pkg', models.ForeignKey(to='utl_files.Package')),
            ],
            options={
                'verbose_name': 'Package Properties',
            },
        ),
        migrations.AlterUniqueTogether(
            name='packageprops',
            unique_together=set([('pkg', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='packagedep',
            unique_together=set([('pkg', 'dep_name')]),
        ),
    ]
