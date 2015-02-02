# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from pinytoCloud.models import User, Assembly, StoredPublicKey, ApiFunction
from Crypto.Cipher import PKCS1_OAEP
from keyserver.settings import PINYTO_PUBLICKEY
from base64 import b16encode
import json
from pymongo import MongoClient
from pymongo.collection import Collection


class TestApiCall(TestCase):
    def setUp(self):
        self.assembly_user = User(name='foo')
        self.assembly_user.save()
        self.assembly = Assembly(name='bar', author=self.assembly_user, description='')
        self.assembly.save()
        self.user = User(name='hugo')
        self.user.save()
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
        self.hugo_key = StoredPublicKey.create(self.user, n, int(65537))
        self.session = self.user.start_session(self.hugo_key)
        self.user.last_calculation_time = timezone.now()
        self.user.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = b16encode(pinyto_cipher.encrypt(self.session.token))

    def test_no_json(self):
        response = self.client.post(
            reverse('api_call', kwargs={'user_name': 'foo', 'assembly_name': 'bar', 'function_name': 'test'}),
            'wlglml',
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], u'All Pinyto API-calls have to use json. This is not valid JSON data.')

    def test_no_token(self):
        response = self.client.post(
            reverse('api_call', kwargs={'user_name': 'foo', 'assembly_name': 'bar', 'function_name': 'test'}),
            json.dumps({'a': 'b'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], u'Unauthenticated API-calls are not supported. Please supply a token.')

    def test_invalid_token(self):
        response = self.client.post(
            reverse('api_call', kwargs={'user_name': 'foo', 'assembly_name': 'bar', 'function_name': 'test'}),
            json.dumps({'token': 'b'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], u'The token is not in valid base16-format.')

    def test_non_existent_user(self):
        response = self.client.post(
            reverse('api_call', kwargs={'user_name': 'wrongbert', 'assembly_name': 'bar', 'function_name': 'test'}),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], u'The user wrongbert was not found. There can not be an assembly wrongbert/bar.')

    def test_unknown_assembly(self):
        response = self.client.post(
            reverse('api_call', kwargs={'user_name': 'foo', 'assembly_name': 'dideldi', 'function_name': 'test'}),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], u'Assembly not found. Does foo have an Assembly named dideldi?')

    def test_assembly_not_installed(self):
        response = self.client.post(
            reverse('api_call', kwargs={'user_name': 'foo', 'assembly_name': 'bar', 'function_name': 'test'}),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], u'The assembly exists but it is not installed.')

    def test_api_function_does_not_exist(self):
        self.user.installed_assemblies.add(self.assembly)
        response = self.client.post(
            reverse('api_call', kwargs={'user_name': 'foo', 'assembly_name': 'bar', 'function_name': 'test'}),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], u'The assembly foo/bar exists but has no API function "test".')

    def test_successful(self):
        self.user.installed_assemblies.add(self.assembly)
        function = ApiFunction(name='test', code="return json.dumps({'badam': 42})", assembly=self.assembly)
        function.save()
        self.collection = Collection(MongoClient().pinyto, self.user.name)
        response = self.client.post(
            reverse('api_call', kwargs={'user_name': 'foo', 'assembly_name': 'bar', 'function_name': 'test'}),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertIn('badam', res)
        self.assertEqual(res['badam'], 42)