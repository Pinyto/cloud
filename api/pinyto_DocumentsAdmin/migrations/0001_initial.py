# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from pinytoCloud.models import User, Assembly, ApiFunction, initialize_budgets


def create_pinyto_user(apps, schema_editor):
    if User.objects.filter(name='pinyto').count() < 1:
        pinyto_user = User(name='pinyto')
        initialize_budgets(User, pinyto_user)
        pinyto_user.save()


def delete_pinyto_user(apps, schema_editor):
    pinyto_user = User.objects.filter(name='pinyto').all()[0]
    if Assembly.objects.filter(author=pinyto_user).count == 0:
        pinyto_user.delete()


def create_DocumentsAdmin_assembly(apps, schema_editor):
    pinyto_user = User.objects.filter(name='pinyto').all()[0]
    description = "Dieses Assembly gewährt dem Admin-Interface vollen Zugriff auf alle Dokumente in der Datenbank. " + \
                  "Da dieses Assembly auf alle Daten zugreifen kann, sollte es nur mit großer Vorsicht eingesetzt " + \
                  "werden. Ist es nicht installiert, können jedoch über das Admin-Interface keine Daten in der " + \
                  "Datenbank manipuliert werden."
    assembly = Assembly(
        name='DocumentsAdmin',
        author=pinyto_user,
        description=description
    )
    assembly.only_own_data = False
    assembly.save()
    search_code = ""
    search_function = ApiFunction(
        name='search',
        code=search_code,
        assembly=assembly)
    search_function.save()
    save_code = ""
    save_function = ApiFunction(
        name='save',
        code=save_code,
        assembly=assembly
    )
    save_function.save()
    delete_code = ""
    delete_function = ApiFunction(
        name='delete',
        code=delete_code,
        assembly=assembly
    )
    delete_function.save()


def delete_DocumentsAdmin_assembly(apps, schema_editor):
    pinyto_user = User.objects.filter(name='pinyto').all()[0]
    assembly = Assembly.objects.filter(user=pinyto_user).filter(name='DocumentsAdmin').all()[0]
    assembly.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('pinytoCloud', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_pinyto_user, delete_pinyto_user),
        migrations.RunPython(create_DocumentsAdmin_assembly, delete_DocumentsAdmin_assembly)
    ]
