# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from django.test.client import Client
from pymongo import MongoClient
from pymongo.collection import Collection
from service.database import CollectionWrapper
from pinytoCloud.models import User
import json


class TestBBorsalino(TestCase):
    def setUp(self):
        self.bborsalino = User(name='bborsalino')
        self.bborsalino.save()
        self.collection = Collection(MongoClient().pinyto, 'bborsalino')
        backup_collection = Collection(MongoClient().pinyto, 'bborsalino_backup')
        for doc in self.collection.find():
            backup_collection.insert(doc)
        self.collection.drop()
        self.collection = Collection(MongoClient().pinyto, 'bborsalino')
        self.collection_wrapper = CollectionWrapper(self.collection)

    def tearDown(self):
        self.collection.drop()
        self.collection = Collection(MongoClient().pinyto, 'bborsalino')
        backup_collection = Collection(MongoClient().pinyto, 'bborsalino_backup')
        for doc in backup_collection.find():
            self.collection.insert(doc)

    def test_index(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7"}})
        test_client = Client()
        response = test_client.post('/bborsalino/Librarian/index', {'ean': '1234567890123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['index'], [])
        response = test_client.post('/bborsalino/Librarian/index', {'isbn': '978-3-943176-24-7'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['index']), 1)
        self.assertEqual(json.loads(response.content)['index'][0]['data']['isbn'], u'978-3-943176-24-7')
        response = test_client.post('/bborsalino/Librarian/index', {})
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
        response = test_client.post('/bborsalino/Librarian/search', {'searchstring': 'Informatik'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['index']), 2)
        self.assertEqual(json.loads(response.content)['index'][0]['data']['isbn'], u'978-3-8085-3004-7')
        self.assertEqual(json.loads(response.content)['index'][1]['data']['isbn'], u'978-3-8273-7337-3')

    def test_update(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "A"}})
        book = self.collection.find()[0]
        book['data']['place'] = "B"
        book['_id'] = str(book['_id'])
        test_client = Client()
        response = test_client.post('/bborsalino/Librarian/update', {'book': json.dumps(book)})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        book_test = self.collection.find()[0]
        self.assertEqual(book_test['data']['place'], u'B')

    def test_update_all(self):
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "A"}})
        self.collection.insert({"type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "B"}})
        test_client = Client()
        response = test_client.post('/bborsalino/Librarian/update_all', {'book': json.dumps({
            "type": "book", "data": {"isbn": "978-3-943176-24-7", "place": "C"}
        })})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        for book in self.collection.find():
            self.assertEqual(book['data']['place'], u'C')

    def test_duplicate(self):
        pass

    def test_remove(self):
        pass

    def test_statistics(self):
        pass

    def test_job_complete_data_by_asking_dnb(self):
        pass