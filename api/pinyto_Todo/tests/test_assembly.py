# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from django.utils import timezone
from pymongo import MongoClient
from pymongo.collection import Collection
from service.database import CollectionWrapper
from pinytoCloud.models import User, StoredPublicKey, Assembly
from Crypto.Cipher import PKCS1_OAEP
from keyserver.settings import PINYTO_PUBLICKEY
from base64 import b16encode
from datetime import datetime
import json


class TestTodo(TestCase):
    def setUp(self):
        self.pinyto = User(name='pinyto')
        self.pinyto.save()
        if Assembly.objects.filter(name='Todo').filter(author=self.pinyto).count() > 0:
            self.assembly = Assembly.objects.filter(name='Todo').filter(author=self.pinyto).all()[0]
        else:
            self.assembly = Assembly(name='Todo', author=self.pinyto, description='')
            self.assembly.save()
        self.collection = Collection(MongoClient().pinyto, 'Hugo')
        self.collection.remove({})
        self.collection_wrapper = CollectionWrapper(self.collection, 'pinyto/Todo')
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
        self.hugo_key = StoredPublicKey.create(self.hugo, n, int(65537))
        self.session = self.hugo.start_session(self.hugo_key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = str(b16encode(
            pinyto_cipher.encrypt(self.session.token.encode('utf-8'))), encoding='utf-8')

    def test_get_empty_list(self):
        response = self.client.post(
            '/pinyto/Todo/get_list',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('result', res)
        self.assertListEqual(res['result'], [])

    def test_get_list_with_examples(self):
        document1 = {
            'type': 'todo',
            'tags': [],
            'assembly': 'pinyto/Todo',
            'data': 'Wäsche aufhängen'
        }
        document_id = self.collection_wrapper.insert(document1)
        document1['_id'] = document_id
        document1['time'] = datetime(2014, 12, 25, 1, 15, 23, 980169)
        self.collection_wrapper.save(document1)
        self.collection_wrapper.insert({
            'type': 'todo',
            'tags': [],
            'assembly': 'pinyto/Todo',
            'data': 'Zimmer aufräumen'
        })
        response = self.client.post(
            '/pinyto/Todo/get_list',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('result', res)
        for index, document in enumerate(res['result']):
            self.assertEqual(document['type'], 'todo')
            self.assertListEqual(document['tags'], [])
            self.assertEqual(document['assembly'], 'pinyto/Todo')
            self.assertIn('time', document)
            if index == 0:
                data = u'Zimmer aufräumen'
            elif index == 1:
                data = u'Wäsche aufhängen'
            else:
                data = u'Wrong index!'
            self.assertEqual(document['data'], data)

    def test_save_no_json(self):
        response = self.client.post(
            '/pinyto/Todo/save',
            "BlaBlubb",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)

    def test_save_no_document(self):
        response = self.client.post(
            '/pinyto/Todo/save',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], 'You have to supply a document to save.')

    def test_save_no_single_document(self):
        response = self.client.post(
            '/pinyto/Todo/save',
            json.dumps({'token': self.authentication_token, 'document': [{'type': 'fake'}]}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], 'The document you supplied is not a single document. ' +
                                       'Only one document at a time will be saved.')

    def test_save_insert(self):
        response = self.client.post(
            '/pinyto/Todo/save',
            json.dumps({'token': self.authentication_token, 'document': {
                'type': 'todo',
                'tags': [],
                'assembly': 'pinyto/Todo',
                'data': 'Wäsche aufhängen'
            }}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertIn('_id', res)
        self.assertGreater(len(res['_id']), 0)
        self.assertEqual(self.collection_wrapper.count({
            'type': 'todo',
            'tags': [],
            'assembly': 'pinyto/Todo',
            'data': 'Wäsche aufhängen'}), 1)

    def test_save_update(self):
        document_id = self.collection_wrapper.insert({
            'type': 'todo',
            'tags': [],
            'assembly': 'pinyto/Todo',
            'data': 'Zimmer aufräumen'
        })
        response = self.client.post(
            '/pinyto/Todo/save',
            json.dumps({'token': self.authentication_token, 'document': {
                '_id': document_id,
                'type': 'todo',
                'tags': [],
                'assembly': 'pinyto/Todo',
                'data': 'Wäsche aufhängen'
            }}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertIn('_id', res)
        self.assertGreater(len(res['_id']), 0)
        self.assertEqual(self.collection_wrapper.count({
            'type': 'todo',
            'tags': [],
            'assembly': 'pinyto/Todo',
            'data': 'Wäsche aufhängen'}), 1)
        self.assertEqual(self.collection_wrapper.count({
            'type': 'todo',
            'tags': [],
            'assembly': 'pinyto/Todo',
            'data': 'Zimmer aufräumen'}), 0)

    def test_delete_no_json(self):
        response = self.client.post(
            '/pinyto/Todo/delete',
            "BlaBlubb",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)

    def test_delete_no_document(self):
        response = self.client.post(
            '/pinyto/Todo/delete',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], 'You have to supply a document to delete.')

    def test_delete_no_id(self):
        response = self.client.post(
            '/pinyto/Todo/delete',
            json.dumps({'token': self.authentication_token, 'document': {'type': 'todo'}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], 'You have to specify an _id to identify the document you want to delete.')

    def test_delete_wrong_id(self):
        response = self.client.post(
            '/pinyto/Todo/delete',
            json.dumps({'token': self.authentication_token, 'document': {'type': 'todo', '_id': 'ABC123'}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], 'There is no document with this ID. The document could not be deleted.')

    def test_delete_successful(self):
        document_id = self.collection_wrapper.insert({
            'type': 'todo',
            'tags': [],
            'assembly': 'pinyto/Todo',
            'data': 'Zimmer aufräumen'
        })
        response = self.client.post(
            '/pinyto/Todo/delete',
            json.dumps({'token': self.authentication_token, 'document': {'type': 'todo', '_id': document_id}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertEqual(self.collection_wrapper.count({
            'type': 'todo',
            'tags': [],
            'assembly': 'pinyto/Todo',
            'data': 'Zimmer aufräumen'}), 0)