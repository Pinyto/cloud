# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from pinytoCloud.models import User, Assembly, ApiFunction


def create_pinyto_user(apps, schema_editor):
    if User.objects.filter(name='pinyto').count() < 1:
        pinyto_user = User(name='pinyto')
        pinyto_user.save()


def delete_pinyto_user(apps, schema_editor):
    pinyto_user = User.objects.filter(name='pinyto').all()[0]
    if Assembly.objects.filter(author=pinyto_user).count == 0:
        pinyto_user.delete()


def create_Todo_assembly(apps, schema_editor):
    pinyto_user = User.objects.filter(name='pinyto').all()[0]
    description = "This is the assembly for the Pinyto todo apps."
    assembly = Assembly(
        name='Todo',
        author=pinyto_user,
        description=description
    )
    assembly.save()
    get_list_code = "return json.dumps({'result': db.find(\n    query={'type': 'todo'},\n    skip=0,\n    " + \
                    "limit=10000,\n    sorting='time',\n    sort_direction='desc')})"
    get_list_function = ApiFunction(
        name='get_list',
        code=get_list_code,
        assembly=assembly)
    get_list_function.save()
    save_code = "try:\n    request_data = json.loads(request.body)\nexcept ValueError:\n    " + \
                "return json.dumps({'error': 'The request needs to be in JSON format. This was not JSON.'})\n" + \
                "if 'document' not in request_data:\n    " + \
                "return json.dumps({'error': 'You have to supply a document to save.'})\n" + \
                "document = request_data['document']\nif not isinstance(document, dict): \n    " + \
                "return json.dumps({'error': 'The document you supplied is not a single document. ' +" + \
                "\n                                'Only one document at a time will be saved.'})\n" + \
                "if not ('_id' in document and db.count({'_id': document['_id']}) > 0): \n    " + \
                "str_id = db.insert(document)\nelse:\n    str_id = db.save(document)\n" + \
                "return json.dumps({'success': True, '_id': str_id})"
    save_function = ApiFunction(
        name='save',
        code=save_code,
        assembly=assembly
    )
    save_function.save()
    delete_code = "try:\n    request_data = json.loads(request.body)\nexcept ValueError:\n    " + \
                  "return json.dumps({'error': 'The request needs to be in JSON format. This was not JSON.'})\n" + \
                  "if 'document' not in request_data:\n    " + \
                  "return json.dumps({'error': 'You have to supply a document to delete.'})\n" + \
                  "document = request_data['document']\nif '_id' not in document:\n    " + \
                  "return json.dumps({'error': 'You have to specify an _id to identify the document you want to " + \
                  "delete.'})\nif not db.count({'_id': document['_id']}) > 0:\n    " + \
                  "return json.dumps({'error': 'There is no document with this ID. The document could not be " + \
                  "deleted.'})\ndb.remove(document)\nreturn json.dumps({'success': True})"
    delete_function = ApiFunction(
        name='delete',
        code=delete_code,
        assembly=assembly
    )
    delete_function.save()


def delete_Todo_assembly(apps, schema_editor):
    pinyto_user = User.objects.filter(name='pinyto').all()[0]
    assembly = Assembly.objects.filter(user=pinyto_user).filter(name='Todo').all()[0]
    assembly.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('pinytoCloud', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_pinyto_user, delete_pinyto_user),
        migrations.RunPython(create_Todo_assembly, delete_Todo_assembly)
    ]
