# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utl_files', '0010_create_macrodefn_macroref'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='app',
            field=models.ForeignKey(to='utl_files.Application',
                                    help_text="The application to which this package belongs (or 'Global')",
                                    on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='package',
            name='is_certified',
            field=models.BooleanField(help_text='Is officially certified/supported by TownNews.'),
        ),
        migrations.AlterField(
            model_name='package',
            name='name',
            field=models.CharField(max_length=250, help_text='TownNews name for this package.'),
        ),
        migrations.AlterField(
            model_name='package',
            name='version',
            field=models.CharField(max_length=20, help_text='Version number for the package as a whole.'),
        ),
        migrations.AlterField(
            model_name='packagedep',
            name='dep_name',
            field=models.CharField(max_length=200, help_text='The name of the required package'),
        ),
        migrations.AlterField(
            model_name='packagedep',
            name='dep_pkg',
            field=models.ForeignKey(null=True, to='utl_files.Package', related_name='dep_pkg',
                                    help_text='The full data on the required package (opt.)',
                                    on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='packagedep',
            name='dep_version',
            field=models.CharField(max_length=50, help_text='The specific version required.'),
        ),
        migrations.AlterField(
            model_name='packagedep',
            name='pkg',
            field=models.ForeignKey(to='utl_files.Package',
                                    help_text='The package which has this dependency',
                                    on_delete=models.CASCADE),
        ),
    ]
