# coding=utf-8
"""
This File is part of Pinyto
"""
from django.test import TestCase
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.son_manipulator import ObjectId
from service.database import CollectionWrapper
from service.database import encode_underscore_fields, encode_underscore_fields_list


class TestCollectionWrapper(TestCase):
    def setUp(self):
        self.collection = Collection(MongoClient().pinyto, 'collection_wrapper_test')

    def tearDown(self):
        self.collection.drop()

    def test_save(self):
        wrapper = CollectionWrapper(self.collection, assembly_name='some/assembly')
        self.assertEqual(self.collection.find().count(), 0)
        document_prototype = {'a': 9, 'b': 'Test'}
        wrapper.insert(document_prototype)
        document = self.collection.find()[0]
        document['a'] = 1
        wrapper.save(document)
        self.assertEqual(self.collection.find().count(), 1)
        for doc in self.collection.find():
            self.assertEqual(doc['a'], 1)
            self.assertEqual(doc['b'], u'Test')
            self.assertEqual(doc['assembly'], u'some/assembly')

    def test_find(self):
        wrapper = CollectionWrapper(self.collection, assembly_name='some/assembly')
        wrapper.insert({'a': 2, 'b': 'Test'})
        wrapper.insert({'a': 1, 'b': 'Test'})
        self.assertEqual(len(wrapper.find({'a': 1})), 1)
        self.assertEqual(len(wrapper.find({'a': 2})), 1)
        self.assertEqual(len(wrapper.find({'b': 'Test'})), 2)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, skip=1)), 1)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, limit=1)), 1)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, skip=0, sorting='a', sort_direction='asc')), 2)
        for i, doc in enumerate(wrapper.find({'b': 'Test'}, skip=0, sorting='a', sort_direction='asc')):
            self.assertEqual(doc['a'], i + 1)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), str)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, skip=0, sorting='a', sort_direction='desc')), 2)
        for i, doc in enumerate(wrapper.find({'b': 'Test'}, skip=0, sorting='a', sort_direction='desc')):
            self.assertEqual(doc['a'], 2 - i)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), str)

    def test_find_only_own(self):
        self.collection.save({'a': 1, 'b': 'Test'})
        wrapper = CollectionWrapper(self.collection, assembly_name='some/assembly', only_own_data=True)
        wrapper.insert({'a': 2, 'b': 'Test'})
        wrapper.insert({'a': 1, 'b': 'Test'})
        self.assertEqual(len(wrapper.find({'a': 1})), 1)
        self.assertEqual(len(wrapper.find({'a': 2})), 1)
        self.assertEqual(len(wrapper.find({'a': 3})), 0)
        self.assertEqual(len(wrapper.find({'b': 'Test'})), 2)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, skip=1)), 1)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, limit=1)), 1)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, skip=0, sorting='a', sort_direction='asc')), 2)
        for i, doc in enumerate(wrapper.find({'b': 'Test'}, skip=0, sorting='a', sort_direction='asc')):
            self.assertEqual(doc['a'], i + 1)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), str)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, skip=0, sorting='a', sort_direction='desc')), 2)
        for i, doc in enumerate(wrapper.find({'b': 'Test'}, skip=0, sorting='a', sort_direction='desc')):
            self.assertEqual(doc['a'], 2 - i)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), str)

    def test_find_not_only_own(self):
        self.collection.save({'a': 3, 'b': 'Test'})
        wrapper = CollectionWrapper(self.collection, assembly_name='some/assembly', only_own_data=False)
        wrapper.insert({'a': 2, 'b': 'Test'})
        wrapper.insert({'a': 1, 'b': 'Test'})
        self.assertEqual(len(wrapper.find({'a': 1})), 1)
        self.assertEqual(len(wrapper.find({'a': 2})), 1)
        self.assertEqual(len(wrapper.find({'a': 3})), 1)
        self.assertEqual(len(wrapper.find({'b': 'Test'})), 3)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, skip=1)), 2)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, limit=1)), 1)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, skip=0, sorting='a', sort_direction='asc')), 3)
        for i, doc in enumerate(wrapper.find({'b': 'Test'}, skip=0, sorting='a', sort_direction='asc')):
            self.assertEqual(doc['a'], i + 1)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), str)
        self.assertEqual(len(wrapper.find({'b': 'Test'}, skip=0, sorting='a', sort_direction='desc')), 3)
        for i, doc in enumerate(wrapper.find({'b': 'Test'}, skip=0, sorting='a', sort_direction='desc')):
            self.assertEqual(doc['a'], 3 - i)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), str)

    def test_find_documents(self):
        wrapper = CollectionWrapper(self.collection, assembly_name='some/assembly')
        wrapper.insert({'a': 2, 'b': 'Test'})
        wrapper.insert({'a': 1, 'b': 'Test'})
        self.assertEqual(len(list(wrapper.find_documents({'a': 1}))), 1)
        self.assertEqual(len(list(wrapper.find_documents({'a': 2}))), 1)
        self.assertEqual(len(list(wrapper.find_documents({'b': 'Test'}))), 2)
        self.assertEqual(len(list(wrapper.find_documents({'b': 'Test'}, skip=1))), 1)
        self.assertEqual(len(list(wrapper.find_documents({'b': 'Test'}, limit=1))), 1)
        self.assertEqual(
            len(list(wrapper.find_documents({'b': 'Test'}, skip=0, sorting='a', sort_direction='asc'))),
            2
        )
        for i, doc in enumerate(wrapper.find_documents({'b': 'Test'}, skip=0, sorting='a', sort_direction='asc')):
            self.assertEqual(doc['a'], i + 1)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), ObjectId)
        self.assertEqual(
            len(list(wrapper.find_documents({'b': 'Test'}, skip=0, sorting='a', sort_direction='desc'))),
            2
        )
        for i, doc in enumerate(wrapper.find_documents({'b': 'Test'}, skip=0, sorting='a', sort_direction='desc')):
            self.assertEqual(doc['a'], 2 - i)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), ObjectId)

    def test_find_documents_only_own(self):
        self.collection.save({'a': 3, 'b': 'Test'})
        wrapper = CollectionWrapper(self.collection, assembly_name='some/assembly', only_own_data=True)
        wrapper.insert({'a': 2, 'b': 'Test'})
        wrapper.insert({'a': 1, 'b': 'Test'})
        self.assertEqual(len(list(wrapper.find_documents({'a': 1}))), 1)
        self.assertEqual(len(list(wrapper.find_documents({'a': 2}))), 1)
        self.assertEqual(len(list(wrapper.find_documents({'a': 3}))), 0)
        self.assertEqual(len(list(wrapper.find_documents({'b': 'Test'}))), 2)
        self.assertEqual(len(list(wrapper.find_documents({'b': 'Test'}, skip=1))), 1)
        self.assertEqual(len(list(wrapper.find_documents({'b': 'Test'}, limit=1))), 1)
        self.assertEqual(
            len(list(wrapper.find_documents({'b': 'Test'}, skip=0, sorting='a', sort_direction='asc'))),
            2
        )
        for i, doc in enumerate(wrapper.find_documents({'b': 'Test'}, skip=0, sorting='a', sort_direction='asc')):
            self.assertEqual(doc['a'], i + 1)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), ObjectId)
        self.assertEqual(
            len(list(wrapper.find_documents({'b': 'Test'}, skip=0, sorting='a', sort_direction='desc'))),
            2
        )
        for i, doc in enumerate(wrapper.find_documents({'b': 'Test'}, skip=0, sorting='a', sort_direction='desc')):
            self.assertEqual(doc['a'], 2 - i)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), ObjectId)

    def test_find_documents_not_only_own(self):
        self.collection.save({'a': 3, 'b': 'Test'})
        wrapper = CollectionWrapper(self.collection, assembly_name='some/assembly', only_own_data=False)
        wrapper.insert({'a': 2, 'b': 'Test'})
        wrapper.insert({'a': 1, 'b': 'Test'})
        self.assertEqual(len(list(wrapper.find_documents({'a': 1}))), 1)
        self.assertEqual(len(list(wrapper.find_documents({'a': 2}))), 1)
        self.assertEqual(len(list(wrapper.find_documents({'a': 3}))), 1)
        self.assertEqual(len(list(wrapper.find_documents({'b': 'Test'}))), 3)
        self.assertEqual(len(list(wrapper.find_documents({'b': 'Test'}, skip=1))), 2)
        self.assertEqual(len(list(wrapper.find_documents({'b': 'Test'}, limit=1))), 1)
        self.assertEqual(
            len(list(wrapper.find_documents({'b': 'Test'}, skip=0, sorting='a', sort_direction='asc'))),
            3
        )
        for i, doc in enumerate(wrapper.find_documents({'b': 'Test'}, skip=0, sorting='a', sort_direction='asc')):
            self.assertEqual(doc['a'], i + 1)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), ObjectId)
        self.assertEqual(
            len(list(wrapper.find_documents({'b': 'Test'}, skip=0, sorting='a', sort_direction='desc'))),
            3
        )
        for i, doc in enumerate(wrapper.find_documents({'b': 'Test'}, skip=0, sorting='a', sort_direction='desc')):
            self.assertEqual(doc['a'], 3 - i)
            self.assertIn('_id', doc)
            self.assertEqual(type(doc['_id']), ObjectId)

    def test_find_document_for_id(self):
        wrapper = CollectionWrapper(self.collection, 'some/assembly')
        wrapper.insert({'a': 2, 'b': 'Test'})
        wrapper.insert({'a': 1, 'b': 'Test'})
        original_document = wrapper.find({'a': 1})[0]
        retrieved_document = wrapper.find_document_for_id(original_document['_id'])
        self.assertEqual(original_document['a'], retrieved_document['a'])
        self.assertEqual(original_document['b'], retrieved_document['b'])
        self.assertEqual(str(original_document['_id']), str(retrieved_document['_id']))

    def test_find_distinct(self):
        wrapper = CollectionWrapper(self.collection, 'some/assembly')
        wrapper.insert({'a': 2, 'b': 'Test'})
        wrapper.insert({'a': 1, 'b': 'Test'})
        self.assertEqual(wrapper.find_distinct({'b': 'Test'}, 'a'), [2, 1])

    def test_count(self):
        wrapper = CollectionWrapper(self.collection, 'some/assembly')
        wrapper.insert({'a': 2, 'b': 'Test'})
        wrapper.insert({'a': 1, 'b': 'Test'})
        wrapper.insert({'a': 2, 'b': 'Test2'})
        self.assertEqual(wrapper.count({'a': 1}), 1)
        self.assertEqual(wrapper.count({'a': 2}), 2)
        self.assertEqual(wrapper.count({'b': 'Test'}), 2)

    def test_insert(self):
        wrapper = CollectionWrapper(self.collection, 'some/assembly')
        wrapper.insert({'a': 1, 'b': 'Test'})
        self.assertEqual(wrapper.count({'a': 1}), 1)
        document = wrapper.find({'a': 1})[0]
        wrapper.insert(document)
        self.assertEqual(wrapper.count({'a': 1}), 2)
        document = wrapper.find({'a': 1})[0]
        document2 = wrapper.find({'a': 1})[1]
        self.assertEqual(document['a'], document2['a'])
        self.assertEqual(document['b'], document2['b'])
        self.assertNotEqual(str(document['_id']), str(document2['_id']))

    def test_remove(self):
        wrapper = CollectionWrapper(self.collection, 'some/assembly')
        wrapper.insert({'a': 2, 'b': 'Test'})
        wrapper.insert({'a': 1, 'b': 'Test'})
        document = wrapper.find({'a': 1})[0]
        self.assertEqual(wrapper.count({'b': 'Test'}), 2)
        wrapper.remove(document)
        self.assertEqual(wrapper.count({'b': 'Test'}), 1)


class TestDatabaseHelpers(TestCase):
    def test_remove_underscore_fields(self):
        data = {'_id': 3825699854,
                'name': "Test",
                'i_count': 13}
        converted = encode_underscore_fields(data)
        self.assertEqual(converted['name'], "Test")
        self.assertEqual(converted['i_count'], 13)

    def test_remove_underscore_fields_list(self):
        data = {'_id': 3825699854,
                'name': "Test",
                'i_count': 13}
        data_list = [data, data, data]
        converted = encode_underscore_fields_list(data_list)
        for obj in converted:
            self.assertEqual(len(obj), 3)