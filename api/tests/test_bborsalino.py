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
        pass

    def test_update(self):
        pass

    def test_update_all(self):
        pass

    def test_duplicate(self):
        pass

    def test_remove(self):
        pass

    def test_statistics(self):
        pass

    def test_job_complete_data_by_asking_dnb(self):
        pass