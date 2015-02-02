# coding=utf-8
"""
This File is part of Pinyto
"""
from django.test import TestCase
from pinytoCloud.models import User
import json


class RegisterTest(TestCase):
    def test_taken_username(self):
        self.hugo = User(name='hugo')
        self.hugo.save()
        response = self.client.post(
            '/register',
            json.dumps({'username': 'hugo', 'public_key': {'N': 1, 'e': 1}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Username hugo is already taken. Try another username.")

    def test_no_username(self):
        response = self.client.post(
            '/register',
            json.dumps({'thing': '42'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with username and public_key.")

    def test_no_key_data(self):
        response = self.client.post(
            '/register',
            json.dumps({'username': 'hugo'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with username and public_key.")

    def test_key_data_in_a_wrong_format(self):
        response = self.client.post(
            '/register',
            json.dumps({'username': 'hugo', 'public_key': {"No": "1", "ne": "1"}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "The public_key is in the wrong format. The key data must consist of an N and an e."
        )

    def test_n_not_a_number(self):
        response = self.client.post(
            '/register',
            json.dumps({'username': 'hugo', 'public_key': {"N": "abc", "e": "1"}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "Factor N in the public key is not a number. It has to be a long integer transferred as a string."
        )

    def test_e_not_a_number(self):
        response = self.client.post(
            '/register',
            json.dumps({'username': 'hugo', 'public_key': {'N': str(pow(2, 3072) - 7458345), 'e': 'xxx'}}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Factor e in the public key is not a number. It has to be a long integer.")

    def test_n_too_small(self):
        response = self.client.post(
            '/register',
            json.dumps({'username': 'hugo', 'public_key': {"N": 3845, "e": 1}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Factor N in the public key is too small. Please use at least 3072 bit.")

    def test_successful_registration(self):
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
        e = "65537"
        response = self.client.post(
            '/register',
            json.dumps({'username': 'hugo', 'public_key': {'N': n, 'e': e}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertEqual(User.objects.filter(name='hugo').count(), 1)
        key = User.objects.filter(name='hugo').all()[0].keys.all()[0].get_key()
        self.assertEqual(key.n, int(n))
        self.assertEqual(key.e, int(e))

    def test_successful_registration_Klaus_Merkert(self):
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
        e = "65537"
        response = self.client.post(
            '/register',
            json.dumps({'username': 'KlausMerkert', 'public_key': {'N': n, 'e': e}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertEqual(User.objects.filter(name='KlausMerkert').count(), 1)
        key = User.objects.filter(name='KlausMerkert').all()[0].keys.all()[0].get_key()
        self.assertEqual(key.n, int(n))
        self.assertEqual(key.e, int(e))