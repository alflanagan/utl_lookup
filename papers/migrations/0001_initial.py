# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewsPaper',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True, help_text='The official name of the newspaper.')),
            ],
        ),
        migrations.CreateModel(
            name='TNSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('URL', models.URLField(max_length=250, unique=True)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('paper', models.ForeignKey(to='papers.NewsPaper', help_text='The paper that owns this site.',
                                            on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Townnews Site',
            },
        ),
    ]
