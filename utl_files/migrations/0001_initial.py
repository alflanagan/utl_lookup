# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=250)),
                ('version', models.CharField(max_length=20)),
                ('is_certified', models.BooleanField()),
                ('app', models.ForeignKey(to='utl_files.Application')),
            ],
        ),
        migrations.CreateModel(
            name='TNSite',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('URL', models.URLField()),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='UTLFile',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='utl_files')),
                ('file_path', models.FilePathField()),
                ('pkg', models.ForeignKey(to='utl_files.Package')),
            ],
        ),
        migrations.AddField(
            model_name='package',
            name='site',
            field=models.ForeignKey(to='utl_files.TNSite'),
        ),
    ]
