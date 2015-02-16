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
from pinytoCloud.models import User, Assembly, ApiFunction, Job


def create_bborsalino_user(apps, schema_editor):
    if User.objects.filter(name='bborsalino').count() < 1:
        bborsalino_user = User(name='bborsalino')
        bborsalino_user.save()


def delete_bborsalino_user(apps, schema_editor):
    bborsalino_user = User.objects.filter(name='bborsalino').all()[0]
    if Assembly.objects.filter(author=bborsalino_user).count == 0:
        bborsalino_user.delete()


def create_Librarian_assembly(apps, schema_editor):
    bborsalino_user = User.objects.filter(name='bborsalino').all()[0]
    description = "Dies ist eine Bibliotheksverwaltung. Sie speichert Dokumente mit type=book in der Datenbank und " + \
                  "lässt dich diese Datensätze leicht erstellen, bearbeiten und löschen. Der große Plusnpunkt " + \
                  "dieses Systems ist der complete-Job, der Bücher bei denen nur ISBN oder EAN angegeben sind " + \
                  "automatisch beim Online-Katalog der deutschen Nationalbibliothek nachschlägt und mit den " + \
                  "Informationen von dort den Datensatz verkomplettiert."
    assembly = Assembly(
        name='Librarian',
        author=bborsalino_user,
        description=description
    )
    assembly.save()
    functions = [
        ('index', "ean = request.POST.get('ean')\nisbn = request.POST.get('isbn')\nif ean:\n" +
         "    books = db.find({'type': 'book', 'data.ean': ean}, 42)\nelif isbn:\n" +
         "    books = db.find({'type': 'book', 'data.isbn': isbn}, 42)\nelse:\n" +
         "    books = db.find({'type': 'book'}, 42)\nreturn json.dumps({'index': books})"),
        ('search', "search_string = request.POST.get('searchstring')\n" +
         "books = db.find({'type': 'book',\n" +
         "                 'data': {'$exists': True},\n                 '$or': [\n" +
         "                     {'data.title': {'$regex': search_string, '$options': 'i'}},\n" +
         "                     {'data.uniform_title': {'$regex': search_string, '$options': 'i'}},\n" +
         "                     {'data.publisher': {'$regex': search_string, '$options': 'i'}},\n" +
         "                     {'data.year': {'$regex': search_string, '$options': 'i'}},\n" +
         "                     {'data.category': {'$regex': search_string, '$options': 'i'}},\n" +
         "                     {'data.author': {'$regex': search_string, '$options': 'i'}}\n" +
         "                 ]}, 42)\n" +
         "return json.dumps({'index': books})"),
        ('update', "try:\n    book_data = json.loads(request.POST['book'])\nexcept IndexError:\n" +
         "    return json.dumps({'error': 'You have to supply a book to update.'})\nexcept ValueError:\n" +
         "    return json.dumps({'error': 'The data you supplied is not valid json.'})\nif not 'type' in book_data:\n" +
         "    return json.dumps({'error': " +
         "'The data you supplied has no type. Please supply a book with type=book.'})\n" +
         "if book_data['type'] != 'book':\n" +
         "    return json.dumps({'error': 'This is not a book.'})\n" +
         "if not '_id' in book_data:\n" +
         "    return json.dumps({'error': 'You have to specify an _id to identify the book you want to update.'})\n" +
         "book = db.find_document_for_id(book_data['_id'])\nif not book:  # there was an error\n" +
         "    return json.dumps({'error': 'There is no book with this ID which could be updated.'})\n" +
         "for key in book_data['data']:\n    book['data'][key] = book_data['data'][key]\ndb.save(book)\n" +
         "return json.dumps({'success': True})"),
        ('update_all', "try:\n    book_data = json.loads(request.POST['book'])\nexcept IndexError:\n" +
         "    return json.dumps({'error': 'You have to supply a book to update.'})\nexcept ValueError:\n" +
         "    return json.dumps({'error': 'The data you supplied is not valid json.'})\nif not 'type' in book_data:\n" +
         "    return json.dumps({'error': " +
         "'The data you supplied has no type. Please supply a book with type=book.'})\n" +
         "if book_data['type'] != 'book':\n" +
         "    return json.dumps({'error': 'This is not a book.'})\n" +
         "if 'isbn' in book_data['data']:\n" +
         "    books = list(db.find_documents({'type': 'book',\n" +
         "                                    'data': {'$exists': True},\n" +
         "                                    'data.isbn': book_data['data']['isbn']}))\n" +
         "elif 'ean' in book_data['data']:\n" +
         "    books = list(db.find_documents({'type': 'book',\n" +
         "                                    'data': {'$exists': True},\n" +
         "                                    'data.ean': book_data['data']['ean']}))\n" +
         "else:\n    books = []\nif not books:  # there was an error\n" +
         "    return json.dumps({'error': 'There are no books with this ISBN or EAN which could be updated.'})\n" +
         "for key in book_data['data']:\n    for book in books:\n" +
         "        book['data'][key] = book_data['data'][key]\nfor book in books:\n" +
         "    db.save(book)\nreturn json.dumps({'success': True})"),
        ('duplicate', "try:\n    book_data = json.loads(request.POST['book'])\nexcept IndexError:\n" +
         "    return json.dumps({'error': 'You have to supply a book to duplicate.'})\nexcept ValueError:\n" +
         "    return json.dumps({'error': 'The data you supplied is not valid json.'})\n" +
         "if book_data['type'] != 'book':\n    return json.dumps({'error': 'This is not a book.'})\n" +
         "if not '_id' in book_data:\n" +
         "    return json.dumps({'error': " +
         "'You have to specify an _id to identify the book you want to duplicate.'})\n" +
         "book = db.find_document_for_id(book_data['_id'])\nif not book:  # there was an error\n" +
         "    return json.dumps({'error': 'There is no book with this ID which could be updated.'})\n" +
         "for key in book_data['data']:\n    book['data'][key] = book_data['data'][key]\ndb.insert(book)\n" +
         "return json.dumps({'success': True})"),
        ('remove', "try:\n    book_data = json.loads(request.POST['book'])\nexcept IndexError:\n" +
         "    return json.dumps({'error': 'You have to supply a book to remove.'})\nexcept ValueError:\n" +
         "    return json.dumps({'error': 'The data you supplied is not valid json.'})\n" +
         "if book_data['type'] != 'book':\n    return json.dumps({'error': 'This is not a book.'})\n" +
         "if not '_id' in book_data:\n" +
         "    return json.dumps({'error': 'You have to specify an _id to identify the book you want to remove.'})\n" +
         "book = db.find_document_for_id(book_data['_id'])\nif not book:  # there was an error\n" +
         "    return json.dumps({'error': 'There is no book with this ID which could be deleted.'})\n" +
         "db.remove(book)\nreturn json.dumps({'success': True})"),
        ('statistics', "return json.dumps({\n    'book_count': db.count({'type': 'book'}),\n" +
         "    'places_used': db.find_distinct(\n        {'type': 'book', 'data': {'$exists': True}}, 'data.place'),\n" +
         "    'lent_count': db.count({'type': 'book',\n                            'data': {'$exists': True},\n" +
         "                            'data.lent': {'$exists': True, '$ne': ''}})\n})")
    ]
    for name, code in functions:
        function = ApiFunction(name=name, code=code, assembly=assembly)
        function.save()
    job = Job(
        name='job_complete_data_by_asking_dnb',
        code="incomplete_books = db.find_documents({'type': 'book',\n" +
             "                                      'data': {'$exists': True},\n" +
             "                                      '$or': [\n" +
             "                                          {'data.author': {'$exists': False}},\n" +
             "                                          {'data.title': {'$exists': False}},\n" +
             "                                          {'data.uniform_title': {'$exists': False}},\n" +
             "                                          {'data.isbn': {'$exists': False}},\n" +
             "                                          {'data.ean': {'$exists': False}}\n" +
             "                                      ]})\n" +
             "https = factory.create('Https')\n" +
             "for book in incomplete_books:\n" +
             "    query = ''\n" +
             "    if 'isbn' in book['data']:\n" +
             "        query = book['data']['isbn']\n" +
             "    if 'ean' in book['data']:\n" +
             "        query = book['data']['ean']\n" +
             "    content = https.get('portal.dnb.de', '/opac.htm?query=' + query + '&method=simpleSearch')\n" +
             "    if not content:\n        continue\n" +
             "    soup = factory.create('ParseHtml', content)\n" +
             "    if not soup.contains([\n" +
             "        {'tag': 'table',\n" +
             "         'attrs': {'summary': 'Vollanzeige des Suchergebnises'}}  # They have a typo here!\n" +
             "    ]):\n" +
             "        # we probably found a list of results. lets check for that\n" +
             "        link = soup.find_element_and_get_attribute_value(\n" +
             "            [{'tag': 'table', 'attrs': {'summary': 'Suchergebnis'}},  # They have a typo here too!\n" +
             "             {'tag': 'a'}],\n" +
             "            'href')\n" +
             "        if link:\n" +
             "            content = https.get('portal.dnb.de', link)\n" +
             "            soup = factory.create('ParseHtml', content)\n" +
             "    parsed = soup.find_element_and_collect_table_like_information(\n" +
             "        [\n" +
             "            {'tag': 'table',\n" +
             "             'attrs': {\n" +
             "                 'summary': 'Vollanzeige des Suchergebnises'}},\n" +
             "            # They have a typo here!\n" +
             "            {'tag': 'tr'}\n" +
             "        ], {'author': {'search tag': 'td', 'captions': ['Person(en)'], 'content tag': 'td'},\n" +
             "            'title': {'search tag': 'td',\n" +
             "                      'captions': [\n" +
             "                          'Mehrteiliges Werk',\n" +
             "                          'Titel',\n" +
             "                          'Titel/Bezeichnung'],\n" +
             "                      'content tag': 'td'},\n" +
             "            'uniform title': {'search tag': 'td', 'captions': ['Einheitssachtitel'], " +
             "'content tag': 'td'},\n" +
             "            'year': {'search tag': 'td', 'captions': ['Erscheinungsjahr'], 'content tag': 'td'},\n" +
             "            'languages': {'search tag': 'td', 'captions': ['Sprache(n)'], 'content tag': 'td'},\n" +
             "            'category': {'search tag': 'td', 'captions': ['Sachgruppe(n)'], 'content tag': 'td'},\n" +
             "            'publisher': {'search tag': 'td', 'captions': ['Verleger'], 'content tag': 'td'},\n" +
             "            'edition': {'search tag': 'td', 'captions': ['Ausgabe'], 'content tag': 'td'},\n" +
             "            'isbn': {'search tag': 'td', 'captions': ['ISBN/Einband/Preis'], 'content tag': 'td'},\n" +
             "            'ean': {'search tag': 'td', 'captions': ['EAN'], 'content tag': 'td'}\n" +
             "        }\n" +
             "    )\n" +
             "    for key in parsed:\n" +
             "        if not key in book['data']:\n" +
             "            book['data'][key] = parsed[key]\n" +
             "    db.save(book)",
        schedule=0,
        assembly=assembly)
    job.save()


def delete_Librarian_assembly(apps, schema_editor):
    bborsalino_user = User.objects.filter(name='bborsalino').all()[0]
    assembly = Assembly.objects.filter(user=bborsalino_user).filter(name='Librarian').all()[0]
    assembly.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('pinytoCloud', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_bborsalino_user, delete_bborsalino_user),
        migrations.RunPython(create_Librarian_assembly, delete_Librarian_assembly)
    ]
