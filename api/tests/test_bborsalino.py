# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from mock import patch
from django.test.client import Client
from pymongo import MongoClient
from pymongo.collection import Collection
from service.database import CollectionWrapper
from pinytoCloud.models import User, StoredPublicKey, Assembly, ApiFunction, Job
import json


class TestBBorsalino(TestCase):
    def setUp(self):
        self.bborsalino = User(name='bborsalino')
        self.bborsalino.save()
        self.collection = Collection(MongoClient().pinyto, 'Hugo')
        backup_collection = Collection(MongoClient().pinyto, 'Hugo_backup')
        for doc in self.collection.find():
            backup_collection.insert(doc)
        self.collection.drop()
        self.collection = Collection(MongoClient().pinyto, 'Hugo')
        self.collection_wrapper = CollectionWrapper(self.collection)

    def tearDown(self):
        self.collection.drop()
        self.collection = Collection(MongoClient().pinyto, 'Hugo')
        backup_collection = Collection(MongoClient().pinyto, 'Hugo_backup')
        for doc in backup_collection.find():
            self.collection.insert(doc)

    def mock_check_token(self):
        """
        Mocks the token check.
        @return: Session
        """
        hugo = User(name='Hugo')
        hugo.save()
        key = StoredPublicKey.create(hugo, '13', 5)
        return hugo.start_session(key)

    @patch('pinytoCloud.checktoken.check_token', mock_check_token)
    def test_index(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7"}})
        test_client = Client()
        response = test_client.post('/bborsalino/Librarian/index', {'token': 'fake', 'ean': '1234567890123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['index'], [])
        response = test_client.post('/bborsalino/Librarian/index', {'token': 'fake', 'isbn': '978-3-943176-24-7'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['index']), 1)
        self.assertEqual(json.loads(response.content)['index'][0]['data']['isbn'], u'978-3-943176-24-7')
        response = test_client.post('/bborsalino/Librarian/index', {'token': 'fake'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['index']), 1)
        self.assertEqual(json.loads(response.content)['index'][0]['data']['isbn'], u'978-3-943176-24-7')

    @patch('pinytoCloud.checktoken.check_token', mock_check_token)
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
        response = test_client.post('/bborsalino/Librarian/search', {'token': 'fake', 'searchstring': 'Informatik'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['index']), 2)
        self.assertEqual(json.loads(response.content)['index'][0]['data']['isbn'], u'978-3-8085-3004-7')
        self.assertEqual(json.loads(response.content)['index'][1]['data']['isbn'], u'978-3-8273-7337-3')

    @patch('pinytoCloud.checktoken.check_token', mock_check_token)
    def test_update(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "A"}})
        book = self.collection.find_one()
        book['data']['place'] = "B"
        book['_id'] = str(book['_id'])
        test_client = Client()
        response = test_client.post('/bborsalino/Librarian/update', {'token': 'fake', 'book': json.dumps(book)})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        book_test = self.collection.find()[0]
        self.assertEqual(book_test['data']['place'], u'B')

    @patch('pinytoCloud.checktoken.check_token', mock_check_token)
    def test_update_all(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "A"}})
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "B"}})
        test_client = Client()
        response = test_client.post('/bborsalino/Librarian/update_all', {'token': 'fake', 'book': json.dumps({
            "type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "C"}
        })})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        for book in self.collection.find():
            self.assertEqual(book['data']['place'], u'C')

    @patch('pinytoCloud.checktoken.check_token', mock_check_token)
    def test_duplicate(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "author": "Max Mustermann"}})
        book = self.collection.find_one()
        del book['data']['author']
        self.assertFalse('author' in book['data'])
        book['_id'] = str(book['_id'])
        test_client = Client()
        response = test_client.post('/bborsalino/Librarian/duplicate', {'token': 'fake', 'book': json.dumps(book)})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        self.assertEqual(self.collection.find(
            {'type': "book", 'data': {'$exists': True}, 'data.isbn': "978-3-943176-24-7"}
        ).count(), 2)
        for book in self.collection.find({"type": "book", 'data.isbn': "978-3-943176-24-7"}):
            self.assertEqual(book['data']['isbn'], u'978-3-943176-24-7')
            self.assertEqual(book['data']['author'], u'Max Mustermann')

    @patch('pinytoCloud.checktoken.check_token', mock_check_token)
    def test_remove(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "author": "Max Mustermann"}})
        self.assertEqual(self.collection.find({'type': "book"}).count(), 1)
        book = self.collection.find_one()
        book['_id'] = str(book['_id'])
        test_client = Client()
        response = test_client.post('/bborsalino/Librarian/remove', {'token': 'fake', 'book': json.dumps(book)})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        self.assertEqual(self.collection.find({'type': "book"}).count(), 0)

    @patch('pinytoCloud.checktoken.check_token', mock_check_token)
    def test_statistics(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "A"}})
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "B", "lent": "Hugo"}})
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-8085-3004-7", "place": "C"}})
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-8273-7337-3", "place": "B"}})
        test_client = Client()
        response = test_client.post('/bborsalino/Librarian/statistics', {'token': 'fake'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertEqual(res['book_count'], 4)
        self.assertEqual(res['places_used'], [u'A', u'B', u'C'])
        self.assertEqual(res['lent_count'], 1)

    def test_job_complete_data_by_asking_dnb(self):
        pass


class TestBBorsalinoSandbox(TestCase):
    def setUp(self):
        self.bborsalino = User(name='bborsalinosandbox')
        self.bborsalino.save()
        self.assembly = Assembly(name='Librarian', author=self.bborsalino, description="Manage your books.")
        self.assembly.save()
        self.librarian_index = ApiFunction(name='index', code="""ean = request.POST.get('ean')
isbn = request.POST.get('isbn')
if ean:
    books = db.find({'type': 'book', 'data.ean': ean}, 42)
elif isbn:
    books = db.find({'type': 'book', 'data.isbn': isbn}, 42)
else:
    books = db.find({'type': 'book'}, 42)
return json.dumps({'index': books})""", assembly=self.assembly)
        self.librarian_index.save()

        self.collection = Collection(MongoClient().pinyto, 'Hugo')
        backup_collection = Collection(MongoClient().pinyto, 'Hugo_backup')
        for doc in self.collection.find():
            backup_collection.insert(doc)
        self.collection.drop()
        self.collection = Collection(MongoClient().pinyto, 'Hugo')
        self.collection_wrapper = CollectionWrapper(self.collection)

    def tearDown(self):
        self.collection.drop()
        self.collection = Collection(MongoClient().pinyto, 'Hugo')
        backup_collection = Collection(MongoClient().pinyto, 'Hugo_backup')
        for doc in backup_collection.find():
            self.collection.insert(doc)

    def mock_check_token(self):
        """
        Mocks the token check.
        @return: Session
        """
        hugo = User(name='Hugo')
        hugo.save()
        key = StoredPublicKey.create(hugo, '13', 5)
        return hugo.start_session(key)

    @patch('pinytoCloud.checktoken.check_token', mock_check_token)
    def test_index(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7"}})
        test_client = Client()
        response = test_client.post('/bborsalinosandbox/Librarian/index', {'token': 'fake', 'ean': '1234567890123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['index'], [])
        response = test_client.post('/bborsalinosandbox/Librarian/index', {'token': 'fake', 'isbn': '978-3-943176-24-7'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['index']), 1)
        self.assertEqual(json.loads(response.content)['index'][0]['data']['isbn'], u'978-3-943176-24-7')
        response = test_client.post('/bborsalinosandbox/Librarian/index', {'token': 'fake'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['index']), 1)
        self.assertEqual(json.loads(response.content)['index'][0]['data']['isbn'], u'978-3-943176-24-7')