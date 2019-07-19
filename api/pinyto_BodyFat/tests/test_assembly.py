# coding=utf-8
"""
Pinyto cloud - A secure cloud database for your personal data
Copyright (C) 2019 Pina Merkert <pina@pinae.net>

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
from database.mongo_connection import MongoConnection
from pymongo.collection import Collection
from service.database import CollectionWrapper
from pinytoCloud.models import User, StoredPublicKey, Assembly
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from keyserver.settings import PINYTO_PUBLIC_KEY
from base64 import b64encode
from datetime import datetime
import json


class TestBodyFat(TestCase):
    def setUp(self):
        self.pinyto = User(name='pinyto')
        self.pinyto.save()
        if Assembly.objects.filter(name='BodyFat').filter(author=self.pinyto).count() > 0:
            self.assembly = Assembly.objects.filter(name='BodyFat').filter(author=self.pinyto).all()[0]
        else:
            self.assembly = Assembly(name='BodyFat', author=self.pinyto, description='')
            self.assembly.save()
        self.collection = Collection(MongoConnection.get_db(), 'Hugo')
        self.collection.delete_many({})
        self.collection_wrapper = CollectionWrapper(self.collection, 'pinyto/BodyFat')
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

    def test_empty_history(self):
        response = self.client.post(
            '/pinyto/BodyFat/load_fat_history',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('result', res)
        self.assertListEqual(res['result'], [])

    def test_get_list_with_examples(self):
        document1 = {
            'type': 'body_fat',
            'tags': [],
            'assembly': 'pinyto/BodyFat',
            'data': {'fat_percentage': 16.32}
        }
        document_id = self.collection_wrapper.insert(document1)
        document1['_id'] = document_id
        document1['time'] = datetime(2019, 7, 17, 16, 42, 23, 980169)
        self.collection_wrapper.save(document1)
        self.collection_wrapper.insert({
            'type': 'body_fat',
            'tags': [],
            'assembly': 'pinyto/BodyFat',
            'data': {'fat_percentage': 15.71}
        })
        response = self.client.post(
            '/pinyto/BodyFat/load_fat_history',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('result', res)
        for index, document in enumerate(res['result']):
            self.assertEqual(document['type'], 'body_fat')
            self.assertListEqual(document['tags'], [])
            self.assertEqual(document['assembly'], 'pinyto/BodyFat')
            self.assertIn('time', document)
            if index == 0:
                data = {'fat_percentage': 16.32}
            elif index == 1:
                data = {'fat_percentage': 15.71}
            else:
                data = 'Wrong index!'
            self.assertEqual(document['data'], data)

    def test_save_no_json(self):
        response = self.client.post(
            '/pinyto/BodyFat/save',
            "BlaBlubb",
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)

    def test_save_no_document(self):
        response = self.client.post(
            '/pinyto/BodyFat/save',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], 'You have to supply a document to save.')

    def test_save_no_single_document(self):
        response = self.client.post(
            '/pinyto/BodyFat/save',
            json.dumps({'token': self.authentication_token, 'document': [{'type': 'fake'}]}),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], 'The document you supplied is not a single document. ' +
                                       'Only one document at a time will be saved.')

    def test_save_insert(self):
        response = self.client.post(
            '/pinyto/BodyFat/save',
            json.dumps({'token': self.authentication_token, 'document': {
                'type': 'body_fat',
                'tags': [],
                'assembly': 'pinyto/BodyFat',
                'data': {'fat_percentage': 17.01}
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
            'type': 'body_fat',
            'tags': [],
            'assembly': 'pinyto/BodyFat',
            'data': {'fat_percentage': 17.01}}), 1)

    def test_save_update(self):
        document1 = {
            'type': 'body_fat',
            'tags': [],
            'assembly': 'pinyto/BodyFat',
            'data': {'fat_percentage': 14.2}
        }
        document_id = self.collection_wrapper.insert(document1)
        document1['_id'] = document_id
        document1['time'] = datetime(2019, 7, 17, 16, 42, 23, 980169)
        self.collection_wrapper.save(document1)
        document2 = {
            '_id': document_id,
            'type': 'body_fat',
            'tags': [],
            'assembly': 'pinyto/BodyFat',
            'data': {'fat_percentage': 16.42},
            'time': datetime(2019, 7, 15, 16, 42, 23, 980169).timestamp()}
        response = self.client.post(
            '/pinyto/BodyFat/save',
            json.dumps({'token': self.authentication_token, 'document': document2}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertIn('_id', res)
        self.assertGreater(len(res['_id']), 0)
        self.assertEqual(self.collection_wrapper.count({
            'type': 'body_fat',
            'tags': [],
            'assembly': 'pinyto/BodyFat',
            'data': {'fat_percentage': 16.42}}), 1)
        self.assertEqual(self.collection_wrapper.count({
            'type': 'body_fat',
            'tags': [],
            'assembly': 'pinyto/BodyFat',
            'data': {'fat_percentage': 14.2}}), 0)

    def test_delete_no_json(self):
        response = self.client.post(
            '/pinyto/BodyFat/delete',
            "BlaBlubb",
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)

    def test_delete_no_document(self):
        response = self.client.post(
            '/pinyto/BodyFat/delete',
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], 'You have to supply a document to delete.')

    def test_delete_no_id(self):
        response = self.client.post(
            '/pinyto/BodyFat/delete',
            json.dumps({'token': self.authentication_token, 'document': {'type': 'body_fat'}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], 'You have to specify an _id to identify the ' +
                         'body_fat document you want to delete.')

    def test_delete_wrong_id(self):
        response = self.client.post(
            '/pinyto/BodyFat/delete',
            json.dumps({'token': self.authentication_token, 'document': {'type': 'body_fat', '_id': 'ABC123'}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], 'There is no body_fat reading with this ID. The document could not be deleted.')

    def test_delete_successful(self):
        document_id = self.collection_wrapper.insert({
            'type': 'body_fat',
            'tags': [],
            'assembly': 'pinyto/BodyFat',
            'data': {'fat_percentage': 15.0}
        })
        response = self.client.post(
            '/pinyto/BodyFat/delete',
            json.dumps({'token': self.authentication_token, 'document': {'type': 'body_fat', '_id': document_id}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertEqual(self.collection_wrapper.count({
            'type': 'body_fat',
            'tags': [],
            'assembly': 'pinyto/BodyFat',
            'data': {'fat_percentage': 15.0}}), 0)
