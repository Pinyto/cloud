# coding=utf-8
"""
This File is part of Pinyto
"""

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from pinytoCloud.models import User, StoredPublicKey
from Crypto.Cipher import PKCS1_OAEP
from keyserver.settings import PINYTO_PUBLICKEY
from base64 import b16encode
from django.utils import timezone
import json
import datetime
import time


class StatisticsTest(TestCase):
    def test_no_JSON(self):
        response = self.client.post(
            reverse('statistics'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the token as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('statistics'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token key.")

    def test_successful(self):
        one_second_ago = timezone.now() - datetime.timedelta(seconds=1)
        hugo = User(name='Hugo')
        hugo.save()
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
        key = StoredPublicKey.create(hugo, unicode(n), long(65537))
        session = hugo.start_session(key)
        hugo.last_calculation_time = timezone.now()
        hugo.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        authentication_token = b16encode(pinyto_cipher.encrypt(session.token))
        test_client = Client()
        response = test_client.post(
            reverse('statistics'),
            json.dumps({'token': authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertIn('time_budget', res)
        self.assertIn('storage_budget', res)
        self.assertIn('current_storage', res)
        self.assertIn('last_calculation', res)
        self.assertIn('assembly_count', res)
        self.assertIn('installed_assemblies_count', res)
        self.assertIn('all_assemblies_count', res)
        self.assertAlmostEqual(res['time_budget'], 0)
        self.assertAlmostEqual(res['storage_budget'], 0)
        self.assertAlmostEqual(res['current_storage'], 0)
        self.assertGreaterEqual(
            res['last_calculation'],
            time.mktime((one_second_ago.year, one_second_ago.month, one_second_ago.day,
                        one_second_ago.hour, one_second_ago.minute, one_second_ago.second,
                        -1, -1, -1)) + one_second_ago.microsecond)
        now = timezone.now()
        self.assertLessEqual(
            res['last_calculation'],
            time.mktime((now.year, now.month, now.day,
                        now.hour, now.minute, now.second,
                        -1, -1, -1)) + now.microsecond)
        self.assertAlmostEqual(res['assembly_count'], 0)
        self.assertAlmostEqual(res['installed_assemblies_count'], 0)
        self.assertGreaterEqual(res['all_assemblies_count'], 0)