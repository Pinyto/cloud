# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('name', models.CharField(primary_key=True, serialize=False, max_length=30)),
                ('salt', models.CharField(max_length=10)),
                ('hash_iterations', models.IntegerField(default=42000)),
                ('hash', models.CharField(max_length=32)),
                ('N', models.CharField(max_length=1000)),
                ('e', models.BigIntegerField()),
                ('d', models.CharField(max_length=1000)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
