# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('keyserver', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='p',
            field=models.CharField(max_length=1000, default='0'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='account',
            name='q',
            field=models.CharField(max_length=1000, default='0'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='hash_iterations',
            field=models.IntegerField(default=10000),
            preserve_default=True,
        ),
    ]
