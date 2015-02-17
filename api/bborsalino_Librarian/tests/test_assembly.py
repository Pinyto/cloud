# coding=utf-8
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

from django.test import TestCase
from django.utils import timezone
from django.test.client import Client
from pymongo import MongoClient
from pymongo.collection import Collection
from service.database import CollectionWrapper
from pinytoCloud.models import User, StoredPublicKey, Assembly, ApiFunction, Job
from keyserver.settings import PINYTO_PUBLIC_KEY
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from base64 import b64encode
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
        n = "80786834235044460669753411937934465449277842371520355275448268809309089837103275734276120262061843" + \
            "82040953057160814756443264828420708196667785914026758492555936799036993873203845333283971291988875" + \
            "64905333027288001767527397028650823278786089145167250771444492046507010295794694133677261621634734" + \
            "05530125866297939558090939335515563636796547332684980763946627841908997674328820577941702462224295" + \
            "91023080141214106650675144953027083435110564938220820928723008124580542122172296783376945594581002" + \
            "94489203359057842535940573304150410796515106223801062333873813388035169746762875303718505405319147" + \
            "63735228337847496797585371899274124266365893059261629173457184767477662377120323970103285633002729" + \
            "06306610916001209282507423762805983901839492297409278073872556121027518681896508767926725326050690" + \
            "17999797844603729682647239404910676547202128069245677198953319406711723439170624972901903301563069" + \
            "19761286652039432383585088538999958199754424880085776963455837493275929222001416141247508586228129" + \
            "25104298689977241649388627991284943225755311234565087492683063470680307824466620495884755592349688" + \
            "90514758626359418505446346340443066573322965964230819589016760515701110073871142950630314224844688" + \
            "783674908255012477718172292636924864748621071981918534901"
        self.hugo_key = StoredPublicKey.create(self.hugo, n, int(65537))
        self.session = self.hugo.start_session(self.hugo_key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        self.authentication_token = str(b64encode(PINYTO_PUBLIC_KEY.encrypt(
            self.session.token.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None)
        )), encoding='utf-8')
        self.collection = Collection(MongoClient().pinyto, 'Hugo')
        self.collection.remove({})
        self.collection_wrapper = CollectionWrapper(self.collection, 'bborsalino/Librarian')

    def test_index(self):
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalino/Librarian",
            "data": {"isbn": "978-3-943176-24-7"}
        })
        test_client = Client()
        response = test_client.post(
            '/bborsalino/Librarian/index',
            json.dumps({'token': self.authentication_token, 'ean': '1234567890123'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(str(response.content, encoding='utf-8'))['index'], [])
        response = test_client.post(
            '/bborsalino/Librarian/index',
            json.dumps({'token': self.authentication_token, 'isbn': '978-3-943176-24-7'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(str(response.content, encoding='utf-8'))['index']), 1)
        self.assertEqual(
            json.loads(str(response.content, encoding='utf-8'))['index'][0]['data']['isbn'],
            '978-3-943176-24-7')
        response = test_client.post(
            '/bborsalino/Librarian/index',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(str(response.content, encoding='utf-8'))['index']), 1)
        self.assertEqual(
            json.loads(str(response.content, encoding='utf-8'))['index'][0]['data']['isbn'],
            '978-3-943176-24-7')

    def test_search(self):
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalino/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "author": "Fels, Kerstin ; Fels, Andreas",
                     "ean": "9783943176247", "languages": "Deutsch (ger)",
                     "edition": "6. Aufl., Ausg. 2012", "place": "Schlafzimmer", "year": 2012,
                     "title": "Fettnäpfchenführer. - Meerbusch : Conbook-Verl."}})
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalino/Librarian",
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
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalino/Librarian",
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
        self.assertEqual(len(json.loads(str(response.content, encoding='utf-8'))['index']), 2)
        self.assertEqual(
            json.loads(str(response.content, encoding='utf-8'))['index'][0]['data']['isbn'],
            '978-3-8085-3004-7')
        self.assertEqual(
            json.loads(str(response.content, encoding='utf-8'))['index'][1]['data']['isbn'],
            '978-3-8273-7337-3')

    def test_update(self):
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalino/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "place": "A"}
        })
        book = self.collection.find_one()
        book['data']['place'] = "B"
        book['_id'] = str(book['_id'])
        test_client = Client()
        response = test_client.post(
            '/bborsalino/Librarian/update',
            json.dumps({'token': self.authentication_token, 'book': book}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(str(response.content, encoding='utf-8'))['success'])
        book_test = self.collection.find()[0]
        self.assertEqual(book_test['data']['place'], u'B')

    def test_update_all(self):
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalino/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "place": "A"}})
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalino/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "place": "B"}})
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
        self.assertTrue(json.loads(str(response.content, encoding='utf-8'))['success'])
        for book in self.collection.find():
            self.assertEqual(book['data']['place'], u'C')

    def test_duplicate(self):
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalino/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "author": "Max Mustermann"}
        })
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
        self.assertTrue(json.loads(str(response.content, encoding='utf-8'))['success'])
        self.assertEqual(self.collection.find(
            {'type': "book", 'data': {'$exists': True}, 'data.isbn': "978-3-943176-24-7"}
        ).count(), 2)
        for book in self.collection.find({"type": "book", 'data.isbn': "978-3-943176-24-7"}):
            self.assertEqual(book['data']['isbn'], u'978-3-943176-24-7')
            self.assertEqual(book['data']['author'], u'Max Mustermann')

    def test_remove(self):
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalino/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "author": "Max Mustermann"}
        })
        self.assertEqual(self.collection.find({'type': "book"}).count(), 1)
        book = self.collection.find_one()
        book['_id'] = str(book['_id'])
        test_client = Client()
        response = test_client.post(
            '/bborsalino/Librarian/remove',
            json.dumps({'token': self.authentication_token, 'book': book}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(str(response.content, encoding='utf-8'))['success'])
        self.assertEqual(self.collection.find({'type': "book"}).count(), 0)

    def test_statistics(self):
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalino/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "place": "A"}})
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalino/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "place": "B", "lent": "Hugo"}})
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalino/Librarian",
            "data": {"isbn": "978-3-8085-3004-7", "place": "C"}})
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalino/Librarian",
            "data": {"isbn": "978-3-8273-7337-3", "place": "B"}})
        test_client = Client()
        response = test_client.post(
            '/bborsalino/Librarian/statistics',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
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
        self.assertTrue(json.loads(str(response.content, encoding='utf-8'))['success'])
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
        self.assertTrue(json.loads(str(response.content, encoding='utf-8'))['success'])
        response = test_client.post(
            '/bborsalino/Librarian/index',
            json.dumps({'token': self.authentication_token, 'isbn': '978-3-943176-24-7'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(str(response.content, encoding='utf-8'))['index']), 1)
        self.assertEqual(json.loads(str(response.content, encoding='utf-8'))['index'][0]['data']['isbn'],
                         '978-3-943176-24-7')
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
            if len(json.loads(str(response.content, encoding='utf-8'))['index']) >= 1 and \
               'data' in json.loads(str(response.content, encoding='utf-8'))['index'][0] and \
               'title' in json.loads(str(response.content, encoding='utf-8'))['index'][0]['data']:
                completed = True
            else:
                time.sleep(0.1)
        self.assertEqual(
            json.loads(str(response.content, encoding='utf-8'))['index'][0]['data']['title'],
            "Fettnäpfchenführer Japan [Elektronische Ressource] : Die Axt im Chrysanthemenwald / " +
            "Kerstin Fels ; Andreas Fels"
        )


class TestBBorsalinoSandbox(TestCase):
    def setUp(self):
        self.bborsalino = User(name='bborsalinosandbox')
        self.bborsalino.save()
        self.assembly = Assembly(name='Librarian', author=self.bborsalino, description="Manage your books.")
        self.assembly.save()
        self.librarian_index = ApiFunction(name='index', code="""try:
    data = json.loads(str(request.body, encoding='utf-8'))
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
    search_string = json.loads(str(request.body, encoding='utf-8'))['searchstring']
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
    book_data = json.loads(str(request.body, encoding='utf-8'))['book']
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
    book_data = json.loads(str(request.body, encoding='utf-8'))['book']
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
    book_data = json.loads(str(request.body, encoding='utf-8'))['book']
except IndexError:
    return json.dumps({'error': 'You have to supply a book to duplicate.'})
except ValueError:
    return json.dumps({'error': 'The data you supplied is not valid json.'})
if book_data['type'] != 'book':
    return json.dumps({'error': 'This is not a book.'})
if '_id' not in book_data:
    return json.dumps({'error': 'You have to specify an _id to identify the book you want to duplicate.'})
book = db.find_document_for_id(book_data['_id'])
if not book:  # there was an error
    return json.dumps({'error': 'There is no book with this ID which could be updated.'})
for key in book_data['data']:
    book['data'][key] = book_data['data'][key]
db.insert(book)
return json.dumps({'success': True})""", assembly=self.assembly)
        self.librarian_duplicate.save()
        self.librarian_remove = ApiFunction(name='remove', code="""try:
    book_data = json.loads(str(request.body, encoding='utf-8'))['book']
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
        self.librarian_complete = Job(
            name='job_complete_data_by_asking_dnb',
            code="""incomplete_books = db.find_documents({'type': 'book',
                                      'data': {'$exists': True},
                                      '$or': [
                                          {'data.author': {'$exists': False}},
                                          {'data.title': {'$exists': False}},
                                          {'data.uniform_title': {'$exists': False}},
                                          {'data.isbn': {'$exists': False}},
                                          {'data.ean': {'$exists': False}}
                                      ]})
http = factory.create('Http')
for book in incomplete_books:
    query = ''
    if 'isbn' in book['data']:
        query = book['data']['isbn']
    if 'ean' in book['data']:
        query = book['data']['ean']
    content = http.get('https://portal.dnb.de/opac.htm?query=' + query + '&method=simpleSearch')
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
            content = http.get('https://portal.dnb.de' + link)
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
        n = "80786834235044460669753411937934465449277842371520355275448268809309089837103275734276120262061843" + \
            "82040953057160814756443264828420708196667785914026758492555936799036993873203845333283971291988875" + \
            "64905333027288001767527397028650823278786089145167250771444492046507010295794694133677261621634734" + \
            "05530125866297939558090939335515563636796547332684980763946627841908997674328820577941702462224295" + \
            "91023080141214106650675144953027083435110564938220820928723008124580542122172296783376945594581002" + \
            "94489203359057842535940573304150410796515106223801062333873813388035169746762875303718505405319147" + \
            "63735228337847496797585371899274124266365893059261629173457184767477662377120323970103285633002729" + \
            "06306610916001209282507423762805983901839492297409278073872556121027518681896508767926725326050690" + \
            "17999797844603729682647239404910676547202128069245677198953319406711723439170624972901903301563069" + \
            "19761286652039432383585088538999958199754424880085776963455837493275929222001416141247508586228129" + \
            "25104298689977241649388627991284943225755311234565087492683063470680307824466620495884755592349688" + \
            "90514758626359418505446346340443066573322965964230819589016760515701110073871142950630314224844688" + \
            "783674908255012477718172292636924864748621071981918534901"
        self.hugo_key = StoredPublicKey.create(self.hugo, n, int(65537))
        self.session = self.hugo.start_session(self.hugo_key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        self.authentication_token = str(b64encode(PINYTO_PUBLIC_KEY.encrypt(
            self.session.token.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None)
        )), encoding='utf-8')
        self.collection = Collection(MongoClient().pinyto, 'Hugo')
        self.collection.remove({})
        self.collection_wrapper = CollectionWrapper(self.collection, 'bborsalino/Librarian')

    def test_index(self):
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalinosandbox/Librarian",
            "data": {"isbn": "978-3-943176-24-7"}})
        test_client = Client()
        response = test_client.post(
            '/bborsalinosandbox/Librarian/index',
            json.dumps({'token': self.authentication_token, 'ean': '1234567890123'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('index', json.loads(str(response.content, encoding='utf-8')))
        self.assertEqual(json.loads(str(response.content, encoding='utf-8'))['index'], [])
        response = test_client.post(
            '/bborsalinosandbox/Librarian/index',
            json.dumps({'token': self.authentication_token, 'isbn': '978-3-943176-24-7'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('index', json.loads(str(response.content, encoding='utf-8')))
        self.assertEqual(len(json.loads(str(response.content, encoding='utf-8'))['index']), 1)
        self.assertEqual(
            json.loads(str(response.content, encoding='utf-8'))['index'][0]['data']['isbn'],
            '978-3-943176-24-7')
        response = test_client.post(
            '/bborsalinosandbox/Librarian/index',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('index', json.loads(str(response.content, encoding='utf-8')))
        self.assertEqual(len(json.loads(str(response.content, encoding='utf-8'))['index']), 1)
        self.assertEqual(
            json.loads(str(response.content, encoding='utf-8'))['index'][0]['data']['isbn'],
            '978-3-943176-24-7')

    def test_search(self):
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalinosandbox/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "author": "Fels, Kerstin ; Fels, Andreas",
                     "ean": "9783943176247", "languages": "Deutsch (ger)",
                     "edition": "6. Aufl., Ausg. 2012", "place": "Schlafzimmer", "year": 2012,
                     "title": "Fettnäpfchenführer. - Meerbusch : Conbook-Verl."}})
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalinosandbox/Librarian",
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
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalinosandbox/Librarian",
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
        self.assertEqual(len(json.loads(str(response.content, encoding='utf-8'))['index']), 2)
        self.assertEqual(
            json.loads(str(response.content, encoding='utf-8'))['index'][0]['data']['isbn'],
            '978-3-8085-3004-7')
        self.assertEqual(
            json.loads(str(response.content, encoding='utf-8'))['index'][1]['data']['isbn'],
            '978-3-8273-7337-3')

    def test_update(self):
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalinosandbox/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "place": "A"}
        })
        book = self.collection.find_one()
        book['data']['place'] = "B"
        book['_id'] = str(book['_id'])
        test_client = Client()
        response = test_client.post(
            '/bborsalinosandbox/Librarian/update',
            json.dumps({'token': self.authentication_token, 'book': book}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(str(response.content, encoding='utf-8'))['success'])
        book_test = self.collection.find()[0]
        self.assertEqual(book_test['data']['place'], u'B')

    def test_update_all(self):
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalinosandbox/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "place": "A"}
        })
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalinosandbox/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "place": "B"}
        })
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
        self.assertTrue(json.loads(str(response.content, encoding='utf-8'))['success'])
        for book in self.collection.find():
            self.assertEqual(book['data']['place'], u'C')

    def test_duplicate(self):
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalinosandbox/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "author": "Max Mustermann"}
        })
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
        self.assertTrue(json.loads(str(response.content, encoding='utf-8'))['success'])
        self.assertEqual(self.collection.find(
            {'type': "book", 'data': {'$exists': True}, 'data.isbn': "978-3-943176-24-7"}
        ).count(), 2)
        for book in self.collection.find({"type": "book", 'data.isbn': "978-3-943176-24-7"}):
            self.assertEqual(book['data']['isbn'], '978-3-943176-24-7')
            self.assertEqual(book['data']['author'], 'Max Mustermann')

    def test_remove(self):
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalinosandbox/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "author": "Max Mustermann"}
        })
        self.assertEqual(self.collection.find({'type': "book"}).count(), 1)
        book = self.collection.find_one()
        book['_id'] = str(book['_id'])
        test_client = Client()
        response = test_client.post(
            '/bborsalinosandbox/Librarian/remove',
            json.dumps({'token': self.authentication_token, 'book': book}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', json.loads(str(response.content, encoding='utf-8')))
        self.assertTrue(json.loads(str(response.content, encoding='utf-8'))['success'])
        self.assertEqual(self.collection.find({'type': "book"}).count(), 0)

    def test_statistics(self):
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalinosandbox/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "place": "A"}
        })
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalinosandbox/Librarian",
            "data": {"isbn": "978-3-943176-24-7", "place": "B", "lent": "Hugo"}
        })
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalinosandbox/Librarian",
            "data": {"isbn": "978-3-8085-3004-7", "place": "C"}
        })
        self.collection.insert({
            "type": "book",
            "assembly": "bborsalinosandbox/Librarian",
            "data": {"isbn": "978-3-8273-7337-3", "place": "B"}
        })
        test_client = Client()
        response = test_client.post(
            '/bborsalinosandbox/Librarian/statistics',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertEqual(res['book_count'], 4)
        self.assertEqual(res['places_used'], [u'A', u'B', u'C'])
        self.assertEqual(res['lent_count'], 1)

    def test_job_complete_data_by_asking_dnb(self):
        test_client = Client()
        response = test_client.post(
            '/bborsalinosandbox/Librarian/store',
            json.dumps({
                'token': self.authentication_token,
                'type': 'book',
                'data': {"isbn": "978-3-943176-24-7", "place": ""}}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', json.loads(str(response.content, encoding='utf-8')))
        self.assertTrue(json.loads(str(response.content, encoding='utf-8'))['success'])
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
        self.assertIn('success', json.loads(str(response.content, encoding='utf-8')))
        self.assertTrue(json.loads(str(response.content, encoding='utf-8'))['success'])
        response = test_client.post(
            '/bborsalinosandbox/Librarian/index',
            json.dumps({'token': self.authentication_token, 'isbn': '978-3-943176-24-7'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('index', json.loads(str(response.content, encoding='utf-8')))
        self.assertEqual(len(json.loads(str(response.content, encoding='utf-8'))['index']), 1)
        self.assertEqual(
            json.loads(str(response.content, encoding='utf-8'))['index'][0]['data']['isbn'],
            '978-3-943176-24-7')
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
            if 'index' in json.loads(str(response.content, encoding='utf-8')) and \
               len(json.loads(str(response.content, encoding='utf-8'))['index']) >= 1 and \
               'data' in json.loads(str(response.content, encoding='utf-8'))['index'][0] and \
               'title' in json.loads(str(response.content, encoding='utf-8'))['index'][0]['data']:
                completed = True
            else:
                time.sleep(0.1)
        self.assertEqual(
            json.loads(str(response.content, encoding='utf-8'))['index'][0]['data']['title'],
            "Fettnäpfchenführer Japan [Elektronische Ressource] : Die Axt im Chrysanthemenwald / "
            "Kerstin Fels ; Andreas Fels"
        )