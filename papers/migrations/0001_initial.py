# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-21 22:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewsPaper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The official name of the newspaper.', max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TownnewsSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('URL', models.URLField(max_length=250, unique=True)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('paper', models.ForeignKey(help_text='The paper that owns this site.', on_delete=django.db.models.deletion.CASCADE, to='papers.NewsPaper')),
            ],
        ),
    ]
