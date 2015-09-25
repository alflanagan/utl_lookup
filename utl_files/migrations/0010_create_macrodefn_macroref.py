# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0009_remove_site_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='MacroDefinition',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('text', models.TextField(max_length=50000)),
                ('name', models.CharField(max_length=250)),
                ('start', models.IntegerField(help_text='Character offset in file at which macro defintion starts.', null=True)),
                ('end', models.IntegerField(help_text='Character offset in file at which macro definition ends.', null=True)),
                ('line', models.IntegerField(help_text='Line number of macro definition in file.', null=True)),
                ('source', models.ForeignKey(to='utl_files.UTLFile', help_text='The file where the macro is defined.')),
            ],
        ),
        migrations.CreateModel(
            name='MacroRef',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('start', models.IntegerField(help_text='Character offset in source file of first character of macro call.')),
                ('line', models.IntegerField(help_text='Line number of macro call in file.', null=True)),
                ('text', models.CharField(max_length=500, help_text='The actual text of the macro call, with args.')),
                ('macro_name', models.CharField(max_length=250, help_text='The ID or expression identifying the macro to be called.')),
                ('source', models.ForeignKey(to='utl_files.UTLFile')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='macroref',
            unique_together=set([('source', 'start')]),
        ),
        migrations.AlterUniqueTogether(
            name='macrodefinition',
            unique_together=set([('source', 'start')]),
        ),
    ]
