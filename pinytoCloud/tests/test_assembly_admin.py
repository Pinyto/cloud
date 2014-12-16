# coding=utf-8
"""
This File is part of Pinyto
"""
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from pinytoCloud.models import User, StoredPublicKey, Assembly, ApiFunction, Job
from Crypto.Cipher import PKCS1_OAEP
from keyserver.settings import PINYTO_PUBLICKEY
from base64 import b16encode
import json


class TestListOwnAssemblies(TestCase):
    def setUp(self):
        self.hugo = User(name='Hugo')
        self.hugo.save()
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
        key = StoredPublicKey.create(self.hugo, unicode(n), long(65537))
        self.session = self.hugo.start_session(key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = b16encode(pinyto_cipher.encrypt(self.session.token))

    def test_no_JSON(self):
        response = self.client.post(
            reverse('list_own_assemblies'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the token as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('list_own_assemblies'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token key.")

    def test_successful_but_empty(self):
        response = self.client.post(
            reverse('list_own_assemblies'),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertListEqual(res, [])

    def test_successful(self):
        assembly1 = Assembly(
            name='test1',
            author=self.hugo,
            description='test assembly no 1'
        )
        assembly1.save()
        func1 = ApiFunction(
            name='func1',
            code='print("Hallo Welt!")',
            assembly=assembly1
        )
        func1.save()
        func2 = ApiFunction(
            name='func2',
            code='print("Hello World!")',
            assembly=assembly1
        )
        func2.save()
        job1 = Job(
            name='job1',
            code='print("Arbeit.")',
            assembly=assembly1,
            schedule=0
        )
        job1.save()
        assembly2 = Assembly(
            name='test2',
            author=self.hugo,
            description='test assembly no 2'
        )
        assembly2.save()
        response = self.client.post(
            reverse('list_own_assemblies'),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertListEqual(res, [
            {
                u'name': u'test1',
                u'description': u'test assembly no 1',
                u'api_functions': [
                    {
                        u'name': u'func1',
                        u'code': u'print("Hallo Welt!")'
                    },
                    {
                        u'name': u'func2',
                        u'code': u'print("Hello World!")'
                    }
                ],
                u'jobs': [
                    {
                        u'name': u'job1',
                        u'code': u'print("Arbeit.")',
                        u'schedule': 0
                    }
                ]
            },
            {
                u'name': u'test2',
                u'description': u'test assembly no 2',
                u'api_functions': [],
                u'jobs': []
            }
        ])