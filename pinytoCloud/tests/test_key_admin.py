# coding=utf-8
"""
This File is part of Pinyto
"""
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from pinytoCloud.models import User, StoredPublicKey
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Random
from Crypto.PublicKey import RSA
from keyserver.settings import PINYTO_PUBLICKEY
from base64 import b16encode
from hashlib import sha256
import json


class TestListKeys(TestCase):
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
        self.hugo_key = StoredPublicKey.create(self.hugo, unicode(n), long(65537))
        self.session = self.hugo.start_session(self.hugo_key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = b16encode(pinyto_cipher.encrypt(self.session.token))

    def test_no_JSON(self):
        response = self.client.post(
            reverse('list_keys'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the token as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('list_keys'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token key.")

    def test_successful(self):
        response = self.client.post(
            reverse('list_keys'),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertListEqual(res, [{u'key_hash': self.hugo_key.key_hash, u'active': True}])


class TestSetKeyActive(TestCase):
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
        self.hugo_key = StoredPublicKey.create(self.hugo, n, int(65537))
        self.session = self.hugo.start_session(self.hugo_key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = b16encode(pinyto_cipher.encrypt(self.session.token))

    def test_no_JSON(self):
        response = self.client.post(
            reverse('set_key_active'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the token as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('set_key_active'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token key.")

    def test_no_key_hash(self):
        response = self.client.post(
            reverse('set_key_active'),
            json.dumps({
                'token': self.authentication_token,
                'active_state': True}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "You have to supply a key_hash and an active_state.")

    def test_do_not_remove_last_key(self):
        response = self.client.post(
            reverse('set_key_active'),
            json.dumps({
                'token': self.authentication_token,
                'key_hash': self.hugo_key.key_hash,
                'active_state': True
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "You are deactivating your last active key. " +
            "That is in all possible scenarios a bad idea so it will not be done."
        )

    def test_successful_activate(self):
        second_key = RSA.generate(3072, Random.new().read)
        second_key_object = StoredPublicKey.create(self.hugo, unicode(second_key.n), long(second_key.e))
        second_key_object.active = False
        second_key_object.save()
        response = self.client.post(
            reverse('set_key_active'),
            json.dumps({
                'token': self.authentication_token,
                'key_hash': second_key_object.key_hash,
                'active_state': True
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertEqual(StoredPublicKey.objects.filter(key_hash=second_key_object.key_hash).count(), 1)
        self.assertTrue(StoredPublicKey.objects.filter(key_hash=second_key_object.key_hash).all()[0].active)

    def test_successful_deactivate(self):
        second_key = RSA.generate(3072, Random.new().read)
        second_key_object = StoredPublicKey.create(self.hugo, unicode(second_key.n), long(second_key.e))
        second_key_object.active = True
        second_key_object.save()
        response = self.client.post(
            reverse('set_key_active'),
            json.dumps({
                'token': self.authentication_token,
                'key_hash': second_key_object.key_hash,
                'active_state': False
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertEqual(StoredPublicKey.objects.filter(key_hash=second_key_object.key_hash).count(), 1)
        self.assertFalse(StoredPublicKey.objects.filter(key_hash=second_key_object.key_hash).all()[0].active)


class TestDeleteKey(TestCase):
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
        self.hugo_key = StoredPublicKey.create(self.hugo, unicode(n), long(65537))
        self.session = self.hugo.start_session(self.hugo_key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = b16encode(pinyto_cipher.encrypt(self.session.token))

    def test_no_JSON(self):
        response = self.client.post(
            reverse('delete_key'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the token as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('delete_key'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token key.")

    def test_no_key_hash(self):
        response = self.client.post(
            reverse('delete_key'),
            json.dumps({
                'token': self.authentication_token,
                'active_state': True}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "You have to supply a key_hash.")

    def test_do_not_remove_last_key(self):
        response = self.client.post(
            reverse('delete_key'),
            json.dumps({
                'token': self.authentication_token,
                'key_hash': self.hugo_key.key_hash
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "You are deleting your last active key. " +
            "That is in all possible scenarios a bad idea so it will not be done."
        )

    def test_successful(self):
        second_key = RSA.generate(3072, Random.new().read)
        second_key_object = StoredPublicKey.create(self.hugo, unicode(second_key.n), long(second_key.e))
        second_key_object.save()
        self.assertEqual(StoredPublicKey.objects.filter(user=self.hugo).count(), 2)
        response = self.client.post(
            reverse('delete_key'),
            json.dumps({
                'token': self.authentication_token,
                'key_hash': second_key_object.key_hash
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertEqual(StoredPublicKey.objects.filter(user=self.hugo).count(), 1)
        self.assertEqual(StoredPublicKey.objects.filter(user=self.hugo).all()[0].key_hash, self.hugo_key.key_hash)


class TestRegisterNewKey(TestCase):
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
        self.hugo_key = StoredPublicKey.create(self.hugo, unicode(n), long(65537))
        self.session = self.hugo.start_session(self.hugo_key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = b16encode(pinyto_cipher.encrypt(self.session.token))

    def test_no_JSON(self):
        response = self.client.post(
            reverse('register_new_key'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the token and public_key as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('register_new_key'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token and the new public_key.")

    def test_no_public_key(self):
        response = self.client.post(
            reverse('register_new_key'),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token and the new public_key.")

    def test_wrong_session(self):
        response = self.client.post(
            reverse('register_new_key'),
            json.dumps({
                'token': 1234,
                'public_key': {'N': '123423423', 'e': 36754}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "The token is not in valid base16-format.")

    def test_public_key_in_wrong_format(self):
        response = self.client.post(
            reverse('register_new_key'),
            json.dumps({
                'token': self.authentication_token,
                'public_key': {'N': '123423423'}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "The public_key is in the wrong format. The key data must consist of an N and an e.")

    def test_n_not_a_number(self):
        response = self.client.post(
            reverse('register_new_key'),
            json.dumps({
                'token': self.authentication_token,
                'public_key': {'N': 'abc', 'e': 123}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "Factor N in the public key is not a number. " +
            "It has to be a long integer transferred as a string.")

    def test_n_too_small(self):
        response = self.client.post(
            reverse('register_new_key'),
            json.dumps({
                'token': self.authentication_token,
                'public_key': {'N': '123423423', 'e': 123}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "Factor N in the public key is too small. Please use at least 3072 bit.")

    def test_e_not_a_number(self):
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
        response = self.client.post(
            reverse('register_new_key'),
            json.dumps({
                'token': self.authentication_token,
                'public_key': {'N': n, 'e': 'abc'}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "Factor e in the public key is not a number. It has to be a long integer.")

    def test_successful(self):
        n = '3840197893679852692918606668254500814305224109110300386604809089501568330128451270693287377405807' + \
            '8349688228133373836291584605323160558270105832687206170401612633518463308387717910384669232993168' + \
            '1442559559914980761365114280068840027244895148391885992795596597534123054248354754430216877410243' + \
            '4815196337246987075528221943091728609466503904367964491684450694878200832174642098602512079308060' + \
            '7598929544704854453062284108242647046946574206431634444878961506803013785824084556410073855439114' + \
            '6296484761168438287296378904633320837259833128680499844389675351892309997985618975553584367428706' + \
            '3788047240727290363565042493631246680948592955378187850700215348697402776228640031690308519582679' + \
            '8761696066603847443205417385669436351935255692607405079587185651764890942057239056561276210316723' + \
            '3452509771192474923710585836871166714232680397852447088322967304520964632905209022043259815460641' + \
            '1879620686381635333693756994629112595397709175606921'
        e = '65537'
        response = self.client.post(
            reverse('register_new_key'),
            json.dumps({
                'token': self.authentication_token,
                'public_key': {'N': n, 'e': e}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        hasher = sha256()
        hasher.update((n + e).encode('utf-8'))
        key_hash = hasher.hexdigest()[:10]
        self.assertEqual(self.hugo.keys.filter(key_hash=key_hash).count(), 1)