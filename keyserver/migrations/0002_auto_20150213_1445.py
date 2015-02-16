# -*- coding: utf-8 -*-
"""
Pinyto cloud - A secure cloud database for your personal data
Copyright (C) 2105 Johannes Merkert <jonny@pinyto.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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
