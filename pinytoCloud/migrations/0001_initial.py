# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApiFunction',
            fields=[
                ('name', models.CharField(max_length=42, primary_key=True, serialize=False)),
                ('code', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Assembly',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=42)),
                ('description', models.TextField()),
                ('only_own_data', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('name', models.CharField(max_length=42, primary_key=True, serialize=False)),
                ('code', models.TextField()),
                ('schedule', models.IntegerField(default=0)),
                ('assembly', models.ForeignKey(to='pinytoCloud.Assembly', related_name='jobs')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('token', models.CharField(max_length=16)),
                ('timestamp', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoredPublicKey',
            fields=[
                ('key_hash', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('N', models.CharField(max_length=1000)),
                ('e', models.BigIntegerField()),
                ('active', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('name', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('time_budget', models.FloatField()),
                ('storage_budget', models.FloatField()),
                ('current_storage', models.BigIntegerField()),
                ('last_calculation_time', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='storedpublickey',
            name='user',
            field=models.ForeignKey(to='pinytoCloud.User', related_name='keys'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='session',
            name='key',
            field=models.OneToOneField(to='pinytoCloud.StoredPublicKey', related_name='related_session'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='session',
            name='user',
            field=models.ForeignKey(to='pinytoCloud.User', related_name='sessions'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assembly',
            name='author',
            field=models.ForeignKey(to='pinytoCloud.User', related_name='assemblies'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assembly',
            name='installed_at',
            field=models.ManyToManyField(to='pinytoCloud.User', related_name='installed_assemblies'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='assembly',
            unique_together=set([('author', 'name')]),
        ),
        migrations.AddField(
            model_name='apifunction',
            name='assembly',
            field=models.ForeignKey(to='pinytoCloud.Assembly', related_name='api_functions'),
            preserve_default=True,
        ),
    ]
