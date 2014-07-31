# coding=utf-8
"""
This File is part of Pinyto
"""
from django.test import TestCase
from pymongo import MongoClient
from pymongo.collection import Collection
from service.database import CollectionWrapper
from service.database import encode_underscore_fields, encode_underscore_fields_list


class TestCollectionWrapper(TestCase):
    def setUp(self):
        self.collection = Collection(MongoClient().pinyto, 'colletion_wrapper_test')

    def tearDown(self):
        self.collection.drop()

    def test_save(self):
        wrapper = CollectionWrapper(self.collection)
        self.assertEqual(self.collection.find().count(), 0)
        document = {'a': 1, 'b': 'Test'}
        wrapper.save(document)
        self.assertEqual(self.collection.find().count(), 1)
        for doc in self.collection.find():
            self.assertEqual(doc['a'], 1)
            self.assertEqual(doc['b'], u'Test')

    def test_find(self):
        wrapper = CollectionWrapper(self.collection)
        wrapper.save({'a': 2, 'b': 'Test'})
        wrapper.save({'a': 1, 'b': 'Test'})
        self.assertEqual(len(wrapper.find({'a': 1})), 1)
        self.assertEqual(len(wrapper.find({'a': 2})), 1)
        self.assertEqual(len(wrapper.find({'b': 'Test'})), 2)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, 1)), 1)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, 0, 'a', 'asc')), 2)
        for i, doc in enumerate(wrapper.find({'b': 'Test'}, 0, 'a', 'asc')):
            self.assertEqual(doc['a'], i + 1)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), str)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, 0, 'a', 'desc')), 2)
        for i, doc in enumerate(wrapper.find({'b': 'Test'}, 0, 'a', 'desc')):
            self.assertEqual(doc['a'], 2 - i)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), str)

    def test_find_documents(self):
        wrapper = CollectionWrapper(self.collection)
        wrapper.save({'a': 2, 'b': 'Test'})
        wrapper.save({'a': 1, 'b': 'Test'})
        self.assertEqual(len(wrapper.find({'a': 1})), 1)
        self.assertEqual(len(wrapper.find({'a': 2})), 1)
        self.assertEqual(len(wrapper.find({'b': 'Test'})), 2)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, 1)), 1)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, 0, 'a', 'asc')), 2)
        for i, doc in enumerate(wrapper.find({'b': 'Test'}, 0, 'a', 'asc')):
            self.assertEqual(doc['a'], i + 1)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), str)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, 0, 'a', 'desc')), 2)
        for i, doc in enumerate(wrapper.find({'b': 'Test'}, 0, 'a', 'desc')):
            self.assertEqual(doc['a'], 2 - i)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), str)

    def test_find_document_for_id(self):
        pass

    def test_count(self):
        pass

    def test_insert(self):
        pass

    def test_remove(self):
        pass


class TestDatabaseHelpers(TestCase):
    def test_remove_underscore_fields(self):
        data = {'_id': 3825699854,
                'name': "Test",
                'i_count': 13}
        converted = encode_underscore_fields(data)
        self.assertEqual(converted['name'], "Test")
        self.assertEqual(converted['i_count'], 13)
        #self.assertNotIn('_id', converted)

    def test_remove_underscore_fields_list(self):
        data = {'_id': 3825699854,
                'name': "Test",
                'i_count': 13}
        data_list = [data, data, data]
        converted = encode_underscore_fields_list(data_list)
        for obj in converted:
            self.assertEqual(len(obj), 3)