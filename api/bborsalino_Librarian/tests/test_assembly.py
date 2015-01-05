# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from django.utils import timezone
from django.test.client import Client
from pymongo import MongoClient
from pymongo.collection import Collection
from service.database import CollectionWrapper
from pinytoCloud.models import User, StoredPublicKey, Assembly, ApiFunction, Job
from Crypto.Cipher import PKCS1_OAEP
from keyserver.settings import PINYTO_PUBLICKEY
from base64 import b16encode
import json
import time


class TestBBorsalino(TestCase):
    def setUp(self):
        self.bborsalino = User(name='bborsalino')
        self.bborsalino.save()
        if Assembly.objects.filter(name='Librarian').filter(author=self.bborsalino).count() > 0:
            self.assembly = Assembly.objects.filter(name='Librarian').filter(author=self.bborsalino).all()[0]
        else:
            self.assembly = Assembly(name='Librarian', author=self.bborsalino, description='')
            self.assembly.save()
        self.hugo = User(name='Hugo')
        self.hugo.save()
        self.hugo.installed_assemblies.add(self.assembly)
        n = "4906219502681250223798809774327327904260276391419666181914677115202847435445452518005507304428444" + \
            "4742603016009120644035348330282759333360784030498937872562985999515117742892991032749465423946790" + \
            "9158556402591029134146090349452893554696956539933811963368734446853075386625683127394662795881747" + \
            "0894364256604860146232603404588092435482734374812471361593625543917217088490113148478038251561381" + \
            "8672330898366008493547872891602227800340728106862543870889614647176014952843513826946064902193374" + \
            "5442573561655969372352609568579364393649500357127004050087969117303304927939643892730600997930439" + \
            "1147195261326440509804663056089132784514383110912100463888066750648282272016554512713401644905102" + \
            "0092897659089644083580577942453555759938724084685541443702341305828164318826796951735041984241803" + \
            "8137353327025799036181291470746401739276004770882613670169229258999662110622086326024782780442603" + \
            "0939464832253228468472307931284129162453821959698949"
        self.hugo_key = StoredPublicKey.create(self.hugo, unicode(n), long(65537))
        self.session = self.hugo.start_session(self.hugo_key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = b16encode(pinyto_cipher.encrypt(self.session.token))
        self.collection = Collection(MongoClient().pinyto, 'Hugo')
        self.collection.remove({})
        self.collection_wrapper = CollectionWrapper(self.collection, 'bborsalino/Librarian')

    def test_index(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7"}})
        test_client = Client()
        response = test_client.post(
            '/bborsalino/Librarian/index',
            json.dumps({'token': self.authentication_token, 'ean': '1234567890123'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['index'], [])
        response = test_client.post(
            '/bborsalino/Librarian/index',
            json.dumps({'token': self.authentication_token, 'isbn': '978-3-943176-24-7'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['index']), 1)
        self.assertEqual(json.loads(response.content)['index'][0]['data']['isbn'], u'978-3-943176-24-7')
        response = test_client.post(
            '/bborsalino/Librarian/index',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['index']), 1)
        self.assertEqual(json.loads(response.content)['index'][0]['data']['isbn'], u'978-3-943176-24-7')

    def test_search(self):
        self.collection.insert({"type": "book",
                                "data": {"isbn": "978-3-943176-24-7", "author": "Fels, Kerstin ; Fels, Andreas",
                                         "ean": "9783943176247", "languages": "Deutsch (ger)",
                                         "edition": "6. Aufl., Ausg. 2012", "place": "Schlafzimmer", "year": 2012,
                                         "title": "Fettnäpfchenführer. - Meerbusch : Conbook-Verl."}})
        self.collection.insert({"type": "book",
                                "data": {"category": "S Schulbücher",
                                         "publisher": "Haan-Gruiten : Verl. Europa-Lehrmittel Nourney, Vollmer",
                                         "isbn": "978-3-8085-3004-7",
                                         "title": "Informatik und Informationstechnik an beruflichen Gymnasien /" +
                                                  " bearb. von Lehrern und Ingenieuren an beruflichen Schulen und" +
                                                  " berufspädagogischen Seminaren. [Autoren: Ralf Bär ...]",
                                         "author": "Bär, Ralf ; Schiemann, Bernd ; Dehler, Elmar ; " +
                                                   "Bischofberger, Gerhard ; Wolf, Thomas ; Hammer, Nikolai",
                                         "languages": "Deutsch (ger)", "edition": "1. aufl., 1. Dr.",
                                         "ean": "9783808530047", "place": "Arbeitszimmer", "year": 2011}})
        self.collection.insert({"type": "book",
                                "data": {"category": "004 Informatik",
                                         "publisher": "München : Addison Wesley in Pearson Education Deutschland",
                                         "isbn": "978-3-8273-7337-3", "author": "Magenheim, Johannes ; Müller, Thomas",
                                         "title": "Informatik macchiato : Cartoon-Kurs für Schüler und Studenten /" +
                                                  " Johannes Magenheim ; Thomas Müller",
                                         "languages": "Deutsch (ger)", "edition": "1. Aufl.", "ean": "9783827373373",
                                         "place": "Arbeitszimmer", "year": 2009}})
        test_client = Client()
        response = test_client.post(
            '/bborsalino/Librarian/search',
            json.dumps({'token': self.authentication_token, 'searchstring': 'Informatik'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['index']), 2)
        self.assertEqual(json.loads(response.content)['index'][0]['data']['isbn'], u'978-3-8085-3004-7')
        self.assertEqual(json.loads(response.content)['index'][1]['data']['isbn'], u'978-3-8273-7337-3')

    def test_update(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "A"}})
        book = self.collection.find_one()
        book['data']['place'] = "B"
        book['_id'] = str(book['_id'])
        test_client = Client()
        response = test_client.post(
            '/bborsalino/Librarian/update',
            json.dumps({'token': self.authentication_token, 'book': book}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        book_test = self.collection.find()[0]
        self.assertEqual(book_test['data']['place'], u'B')

    def test_update_all(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "A"}})
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "B"}})
        test_client = Client()
        response = test_client.post(
            '/bborsalino/Librarian/update_all',
            json.dumps({
                'token': self.authentication_token,
                'book': {
                    "type": "book",
                    "data": {"isbn": "978-3-943176-24-7", "place": "C"}
                }
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        for book in self.collection.find():
            self.assertEqual(book['data']['place'], u'C')

    def test_duplicate(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "author": "Max Mustermann"}})
        book = self.collection.find_one()
        del book['data']['author']
        self.assertFalse('author' in book['data'])
        book['_id'] = str(book['_id'])
        test_client = Client()
        response = test_client.post(
            '/bborsalino/Librarian/duplicate',
            json.dumps({'token': self.authentication_token, 'book': book}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        self.assertEqual(self.collection.find(
            {'type': "book", 'data': {'$exists': True}, 'data.isbn': "978-3-943176-24-7"}
        ).count(), 2)
        for book in self.collection.find({"type": "book", 'data.isbn': "978-3-943176-24-7"}):
            self.assertEqual(book['data']['isbn'], u'978-3-943176-24-7')
            self.assertEqual(book['data']['author'], u'Max Mustermann')

    def test_remove(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "author": "Max Mustermann"}})
        self.assertEqual(self.collection.find({'type': "book"}).count(), 1)
        book = self.collection.find_one()
        book['_id'] = str(book['_id'])
        test_client = Client()
        response = test_client.post(
            '/bborsalino/Librarian/remove',
            json.dumps({'token': self.authentication_token, 'book': book}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        self.assertEqual(self.collection.find({'type': "book"}).count(), 0)

    def test_statistics(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "A"}})
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "B", "lent": "Hugo"}})
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-8085-3004-7", "place": "C"}})
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-8273-7337-3", "place": "B"}})
        test_client = Client()
        response = test_client.post(
            '/bborsalino/Librarian/statistics',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('book_count', res)
        self.assertEqual(res['book_count'], 4)
        self.assertIn('places_used', res)
        self.assertEqual(res['places_used'], [u'A', u'B', u'C'])
        self.assertIn('lent_count', res)
        self.assertEqual(res['lent_count'], 1)

    def test_job_complete_data_by_asking_dnb(self):
        test_client = Client()
        response = test_client.post(
            '/bborsalino/Librarian/store',
            json.dumps({
                'token': self.authentication_token,
                'type': 'book',
                'data': {
                    "isbn": "978-3-943176-24-7",
                    "place": ""}
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        response = test_client.post(
            '/bborsalino/Librarian/store',
            json.dumps({
                'token': self.authentication_token,
                'type': 'job',
                'data': {
                    "assembly_user": "bborsalino",
                    "assembly_name": "Librarian",
                    "job_name": "job_complete_data_by_asking_dnb"}
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        response = test_client.post(
            '/bborsalino/Librarian/index',
            json.dumps({'token': self.authentication_token, 'isbn': '978-3-943176-24-7'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['index']), 1)
        self.assertEqual(json.loads(response.content)['index'][0]['data']['isbn'], u'978-3-943176-24-7')
        # Wait for job to complete
        iterations = 0
        completed = False
        while not completed:
            iterations += 1
            if iterations > 100:
                self.fail("Maximum iterations reached. The data was not completed.")
            response = test_client.post(
                '/bborsalino/Librarian/index',
                json.dumps({'token': self.authentication_token, 'isbn': '978-3-943176-24-7'}),
                content_type='application/json'
            )
            if len(json.loads(response.content)['index']) >= 1 and \
               'data' in json.loads(response.content)['index'][0] and \
               'title' in json.loads(response.content)['index'][0]['data']:
                completed = True
            else:
                time.sleep(0.1)
        self.assertEqual(
            json.loads(response.content)['index'][0]['data']['title'],
            u"Fettnäpfchenführer Japan [Elektronische Ressource] : Die Axt im Chrysanthemenwald / "
            u"Kerstin Fels ; Andreas Fels"
        )


class TestBBorsalinoSandbox(TestCase):
    def setUp(self):
        self.bborsalino = User(name='bborsalinosandbox')
        self.bborsalino.save()
        self.assembly = Assembly(name='Librarian', author=self.bborsalino, description="Manage your books.")
        self.assembly.save()
        self.librarian_index = ApiFunction(name='index', code="""try:
    data = json.loads(request.body)
except ValueError:
    return json.dumps({'error': 'The data you supplied is not valid json.'})
if 'ean' in data:
    books = db.find({'type': 'book', 'data.ean': data['ean']}, 0, 42)
elif 'isbn' in data:
    books = db.find({'type': 'book', 'data.isbn': data['isbn']}, 0, 42)
else:
    books = db.find({'type': 'book'}, 0, 42)
return json.dumps({'index': books})""", assembly=self.assembly)
        self.librarian_index.save()
        self.librarian_search = ApiFunction(name='search', code="""try:
    search_string = json.loads(request.body)['searchstring']
except ValueError:
    return json.dumps({'error': 'The data you supplied is not valid json.'})
except IndexError:
    search_string = ""
books = db.find({'type': 'book',
                 'data': {'$exists': True},
                 '$or': [
                     {'data.title': {'$regex': search_string, '$options': 'i'}},
                     {'data.uniform_title': {'$regex': search_string, '$options': 'i'}},
                     {'data.publisher': {'$regex': search_string, '$options': 'i'}},
                     {'data.year': {'$regex': search_string, '$options': 'i'}},
                     {'data.category': {'$regex': search_string, '$options': 'i'}},
                     {'data.author': {'$regex': search_string, '$options': 'i'}}
                 ]}, 0, 42)
return json.dumps({'index': books})""", assembly=self.assembly)
        self.librarian_search.save()
        self.librarian_update = ApiFunction(name='update', code="""try:
    book_data = json.loads(request.body)['book']
except IndexError:
    return json.dumps({'error': 'You have to supply a book to update.'})
except ValueError:
    return json.dumps({'error': 'The data you supplied is not valid json.'})
if 'type' not in book_data:
    return json.dumps({'error': 'The data you supplied has no type. Please supply a book with type: book.'})
if book_data['type'] != 'book':
    return json.dumps({'error': 'This is not a book.'})
if '_id' not in book_data:
    return json.dumps({'error': 'You have to specify an _id to identify the book you want to update.'})
book = db.find_document_for_id(book_data['_id'])
if not book:  # there was an error
    return json.dumps({'error': 'There is no book with this ID which could be updated.'})
for key in book_data['data']:
    book['data'][key] = book_data['data'][key]
db.save(book)
return json.dumps({'success': True})""", assembly=self.assembly)
        self.librarian_update.save()
        self.librarian_update_all = ApiFunction(name='update_all', code="""try:
    book_data = json.loads(request.body)['book']
except IndexError:
    return json.dumps({'error': 'You have to supply a book to update.'})
except ValueError:
    return json.dumps({'error': 'The data you supplied is not valid json.'})
if 'type' not in book_data:
    return json.dumps({'error': 'The data you supplied has no type. Please supply a book with type: book.'})
if book_data['type'] != 'book':
    return json.dumps({'error': 'This is not a book.'})
if 'isbn' in book_data['data']:
    books = list(db.find_documents({'type': 'book',
                                    'data': {'$exists': True},
                                    'data.isbn': book_data['data']['isbn']}))
elif 'ean' in book_data['data']:
    books = list(db.find_documents({'type': 'book',
                                    'data': {'$exists': True},
                                    'data.ean': book_data['data']['ean']}))
else:
    books = []
if not books:  # there was an error
    return json.dumps({'error': 'There are no books with this ISBN or EAN which could be updated.'})
for key in book_data['data']:
    for book in books:
        book['data'][key] = book_data['data'][key]
for book in books:
    db.save(book)
return json.dumps({'success': True})""", assembly=self.assembly)
        self.librarian_update_all.save()
        self.librarian_duplicate = ApiFunction(name='duplicate', code="""try:
    book_data = json.loads(request.body)['book']
except IndexError:
    return json.dumps({'error': 'You have to supply a book to duplicate.'})
except ValueError:
    return json.dumps({'error': 'The data you supplied is not valid json.'})
if book_data['type'] != 'book':
    return json.dumps({'error': 'This is not a book.'})
if '_id' not in book_data:
    return json.dumps({'error': 'You have to specify an _id to identify the book you want to duplicate.'})
book = db.find_document_for_id(book_data['_id'])
if not book:
    return json.dumps({'error': 'There is no book with this ID which could be updated.'})
for key in book_data['data']:
    book['data'][key] = book_data['data'][key]
db.insert(book)
return json.dumps({'success': True})""", assembly=self.assembly)
        self.librarian_duplicate.save()
        self.librarian_remove = ApiFunction(name='remove', code="""try:
    book_data = json.loads(request.body)['book']
except IndexError:
    return json.dumps({'error': 'You have to supply a book to remove.'})
except ValueError:
    return json.dumps({'error': 'The data you supplied is not valid json.'})
if book_data['type'] != 'book':
    return json.dumps({'error': 'This is not a book.'})
if '_id' not in book_data:
    return json.dumps({'error': 'You have to specify an _id to identify the book you want to remove.'})
book = db.find_document_for_id(book_data['_id'])
if not book:  # there was an error
    return json.dumps({'error': 'There is no book with this ID which could be deleted.'})
db.remove(book)
return json.dumps({'success': True})""", assembly=self.assembly)
        self.librarian_remove.save()
        self.librarian_statistics = ApiFunction(name='statistics', code="""return json.dumps({
    'book_count': db.count({'type': 'book'}),
    'places_used': db.find_distinct(
        {'type': 'book', 'data': {'$exists': True}}, 'data.place'),
    'lent_count': db.count({'type': 'book',
                            'data': {'$exists': True},
                            'data.lent': {'$exists': True, '$ne': ""}})
})""", assembly=self.assembly)
        self.librarian_statistics.save()
        self.librarian_complete = Job(name='job_complete_data_by_asking_dnb', code="""incomplete_books = db.find_documents({'type': 'book',
                                      'data': {'$exists': True},
                                      '$or': [
                                          {'data.author': {'$exists': False}},
                                          {'data.title': {'$exists': False}},
                                          {'data.uniform_title': {'$exists': False}},
                                          {'data.isbn': {'$exists': False}},
                                          {'data.ean': {'$exists': False}}
                                      ]})
https = factory.create('Https')
for book in incomplete_books:
    query = ''
    if 'isbn' in book['data']:
        query = book['data']['isbn']
    if 'ean' in book['data']:
        query = book['data']['ean']
    content = https.get('portal.dnb.de', '/opac.htm?query=' + query + '&method=simpleSearch')
    if not content:
        continue
    soup = factory.create('ParseHtml', content)
    if not soup.contains([
        {'tag': 'table',
         'attrs': {'summary': "Vollanzeige des Suchergebnises"}}  # They have a typo here!
    ]):
        # we probably found a list of results. lets check for that
        link = soup.find_element_and_get_attribute_value(
            [{'tag': 'table', 'attrs': {'summary': "Suchergebnis"}},  # They have a typo here too!
             {'tag': 'a'}],
            'href')
        if link:
            content = https.get('portal.dnb.de', link)
            soup = factory.create('ParseHtml', content)
    parsed = soup.find_element_and_collect_table_like_information(
        [
            {'tag': 'table',
             'attrs': {
                 'summary': "Vollanzeige des Suchergebnises"}},
            # They have a typo here!
            {'tag': 'tr'}
        ], {
            'author': {'search tag': 'td', 'captions': ['Person(en)'], 'content tag': 'td'},
            'title': {'search tag': 'td',
                      'captions': [
                          'Mehrteiliges Werk',
                          'Titel',
                          'Titel/Bezeichnung'],
                      'content tag': 'td'},
            'uniform title': {'search tag': 'td', 'captions': ['Einheitssachtitel'], 'content tag': 'td'},
            'year': {'search tag': 'td', 'captions': ['Erscheinungsjahr'], 'content tag': 'td'},
            'languages': {'search tag': 'td', 'captions': ['Sprache(n)'], 'content tag': 'td'},
            'category': {'search tag': 'td', 'captions': ['Sachgruppe(n)'], 'content tag': 'td'},
            'publisher': {'search tag': 'td', 'captions': ['Verleger'], 'content tag': 'td'},
            'edition': {'search tag': 'td', 'captions': ['Ausgabe'], 'content tag': 'td'},
            'isbn': {'search tag': 'td', 'captions': ['ISBN/Einband/Preis'], 'content tag': 'td'},
            'ean': {'search tag': 'td', 'captions': ['EAN'], 'content tag': 'td'}
        }
    )
    for key in parsed:
        if key not in book['data']:
            book['data'][key] = parsed[key]
    db.save(book)""", assembly=self.assembly, schedule=0)
        self.librarian_complete.save()
        self.hugo = User(name='Hugo')
        self.hugo.save()
        self.hugo.installed_assemblies.add(self.assembly)
        n = "4906219502681250223798809774327327904260276391419666181914677115202847435445452518005507304428444" + \
            "4742603016009120644035348330282759333360784030498937872562985999515117742892991032749465423946790" + \
            "9158556402591029134146090349452893554696956539933811963368734446853075386625683127394662795881747" + \
            "0894364256604860146232603404588092435482734374812471361593625543917217088490113148478038251561381" + \
            "8672330898366008493547872891602227800340728106862543870889614647176014952843513826946064902193374" + \
            "5442573561655969372352609568579364393649500357127004050087969117303304927939643892730600997930439" + \
            "1147195261326440509804663056089132784514383110912100463888066750648282272016554512713401644905102" + \
            "0092897659089644083580577942453555759938724084685541443702341305828164318826796951735041984241803" + \
            "8137353327025799036181291470746401739276004770882613670169229258999662110622086326024782780442603" + \
            "0939464832253228468472307931284129162453821959698949"
        self.hugo_key = StoredPublicKey.create(self.hugo, unicode(n), long(65537))
        self.session = self.hugo.start_session(self.hugo_key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = b16encode(pinyto_cipher.encrypt(self.session.token))
        self.collection = Collection(MongoClient().pinyto, 'Hugo')
        self.collection.remove({})
        self.collection_wrapper = CollectionWrapper(self.collection, 'bborsalino/Librarian')

    def test_index(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7"}})
        test_client = Client()
        response = test_client.post(
            '/bborsalinosandbox/Librarian/index',
            json.dumps({'token': self.authentication_token, 'ean': '1234567890123'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['index'], [])
        response = test_client.post(
            '/bborsalinosandbox/Librarian/index',
            json.dumps({'token': self.authentication_token, 'isbn': '978-3-943176-24-7'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['index']), 1)
        self.assertEqual(json.loads(response.content)['index'][0]['data']['isbn'], u'978-3-943176-24-7')
        response = test_client.post(
            '/bborsalinosandbox/Librarian/index',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['index']), 1)
        self.assertEqual(json.loads(response.content)['index'][0]['data']['isbn'], u'978-3-943176-24-7')

    def test_search(self):
        self.collection.insert({"type": "book",
                                "data": {"isbn": "978-3-943176-24-7", "author": "Fels, Kerstin ; Fels, Andreas",
                                         "ean": "9783943176247", "languages": "Deutsch (ger)",
                                         "edition": "6. Aufl., Ausg. 2012", "place": "Schlafzimmer", "year": 2012,
                                         "title": "Fettnäpfchenführer. - Meerbusch : Conbook-Verl."}})
        self.collection.insert({"type": "book",
                                "data": {"category": "S Schulbücher",
                                         "publisher": "Haan-Gruiten : Verl. Europa-Lehrmittel Nourney, Vollmer",
                                         "isbn": "978-3-8085-3004-7",
                                         "title": "Informatik und Informationstechnik an beruflichen Gymnasien /" +
                                                  " bearb. von Lehrern und Ingenieuren an beruflichen Schulen und" +
                                                  " berufspädagogischen Seminaren. [Autoren: Ralf Bär ...]",
                                         "author": "Bär, Ralf ; Schiemann, Bernd ; Dehler, Elmar ; " +
                                                   "Bischofberger, Gerhard ; Wolf, Thomas ; Hammer, Nikolai",
                                         "languages": "Deutsch (ger)", "edition": "1. aufl., 1. Dr.",
                                         "ean": "9783808530047", "place": "Arbeitszimmer", "year": 2011}})
        self.collection.insert({"type": "book",
                                "data": {"category": "004 Informatik",
                                         "publisher": "München : Addison Wesley in Pearson Education Deutschland",
                                         "isbn": "978-3-8273-7337-3", "author": "Magenheim, Johannes ; Müller, Thomas",
                                         "title": "Informatik macchiato : Cartoon-Kurs für Schüler und Studenten /" +
                                                  " Johannes Magenheim ; Thomas Müller",
                                         "languages": "Deutsch (ger)", "edition": "1. Aufl.", "ean": "9783827373373",
                                         "place": "Arbeitszimmer", "year": 2009}})
        test_client = Client()
        response = test_client.post(
            '/bborsalinosandbox/Librarian/search',
            json.dumps({'token': self.authentication_token, 'searchstring': 'Informatik'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['index']), 2)
        self.assertEqual(json.loads(response.content)['index'][0]['data']['isbn'], u'978-3-8085-3004-7')
        self.assertEqual(json.loads(response.content)['index'][1]['data']['isbn'], u'978-3-8273-7337-3')

    def test_update(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "A"}})
        book = self.collection.find_one()
        book['data']['place'] = "B"
        book['_id'] = str(book['_id'])
        test_client = Client()
        response = test_client.post(
            '/bborsalinosandbox/Librarian/update',
            json.dumps({'token': self.authentication_token, 'book': book}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        book_test = self.collection.find()[0]
        self.assertEqual(book_test['data']['place'], u'B')

    def test_update_all(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "A"}})
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "B"}})
        test_client = Client()
        response = test_client.post(
            '/bborsalinosandbox/Librarian/update_all',
            json.dumps({
                'token': self.authentication_token,
                'book': {
                    "type": "book",
                    "data": {"isbn": "978-3-943176-24-7", "place": "C"}
                }
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        for book in self.collection.find():
            self.assertEqual(book['data']['place'], u'C')

    def test_duplicate(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "author": "Max Mustermann"}})
        book = self.collection.find_one()
        del book['data']['author']
        self.assertFalse('author' in book['data'])
        book['_id'] = str(book['_id'])
        test_client = Client()
        response = test_client.post(
            '/bborsalinosandbox/Librarian/duplicate',
            json.dumps({'token': self.authentication_token, 'book': book}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        self.assertEqual(self.collection.find(
            {'type': "book", 'data': {'$exists': True}, 'data.isbn': "978-3-943176-24-7"}
        ).count(), 2)
        for book in self.collection.find({"type": "book", 'data.isbn': "978-3-943176-24-7"}):
            self.assertEqual(book['data']['isbn'], u'978-3-943176-24-7')
            self.assertEqual(book['data']['author'], u'Max Mustermann')

    def test_remove(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "author": "Max Mustermann"}})
        self.assertEqual(self.collection.find({'type': "book"}).count(), 1)
        book = self.collection.find_one()
        book['_id'] = str(book['_id'])
        test_client = Client()
        response = test_client.post(
            '/bborsalinosandbox/Librarian/remove',
            json.dumps({'token': self.authentication_token, 'book': book}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        self.assertEqual(self.collection.find({'type': "book"}).count(), 0)

    def test_statistics(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "A"}})
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "B", "lent": "Hugo"}})
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-8085-3004-7", "place": "C"}})
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-8273-7337-3", "place": "B"}})
        test_client = Client()
        response = test_client.post(
            '/bborsalinosandbox/Librarian/statistics',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertEqual(res['book_count'], 4)
        self.assertEqual(res['places_used'], [u'A', u'B', u'C'])
        self.assertEqual(res['lent_count'], 1)

    def test_job_complete_data_by_asking_dnb(self):
        test_client = Client()
        response = test_client.post(
            '/bborsalinosandbox/Librarian/store',
            json.dumps({'token': self.authentication_token, 'type': 'book', 'data': {"isbn": "978-3-943176-24-7", "place": ""}}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        response = test_client.post(
            '/bborsalinosandbox/Librarian/store',
            json.dumps({
                'token': self.authentication_token,
                'type': 'job',
                'data': {
                    "assembly_user": "bborsalinosandbox",
                    "assembly_name": "Librarian",
                    "job_name": "job_complete_data_by_asking_dnb"}
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        response = test_client.post(
            '/bborsalinosandbox/Librarian/index',
            json.dumps({'token': self.authentication_token, 'isbn': '978-3-943176-24-7'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['index']), 1)
        self.assertEqual(json.loads(response.content)['index'][0]['data']['isbn'], u'978-3-943176-24-7')
        # Wait for job to complete
        iterations = 0
        completed = False
        while not completed:
            iterations += 1
            if iterations > 100:
                self.fail("Maximum iterations reached. The data was not completed.")
            response = test_client.post(
                '/bborsalinosandbox/Librarian/index',
                json.dumps({'token': self.authentication_token, 'isbn': '978-3-943176-24-7'}),
                content_type='application/json'
            )
            if len(json.loads(response.content)['index']) >= 1 and \
               'data' in json.loads(response.content)['index'][0] and \
               'title' in json.loads(response.content)['index'][0]['data']:
                completed = True
            else:
                time.sleep(0.1)
        self.assertEqual(
            json.loads(response.content)['index'][0]['data']['title'],
            u"Fettnäpfchenführer Japan [Elektronische Ressource] : Die Axt im Chrysanthemenwald / "
            u"Kerstin Fels ; Andreas Fels"
        )