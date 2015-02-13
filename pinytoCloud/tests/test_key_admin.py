# coding=utf-8
"""
This File is part of Pinyto
"""
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from pinytoCloud.models import User, StoredPublicKey
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from keyserver.settings import PINYTO_PUBLIC_KEY
from base64 import b64encode
from hashlib import sha256
import json


class TestListKeys(TestCase):
    def setUp(self):
        self.hugo = User(name='Hugo')
        self.hugo.save()
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

    def test_no_JSON(self):
        response = self.client.post(
            reverse('list_keys'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the token as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('list_keys'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token key.")

    def test_successful(self):
        response = self.client.post(
            reverse('list_keys'),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertListEqual(res, [{u'key_hash': self.hugo_key.key_hash, u'active': True}])


class TestSetKeyActive(TestCase):
    def setUp(self):
        self.hugo = User(name='Hugo')
        self.hugo.save()
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

    def test_no_JSON(self):
        response = self.client.post(
            reverse('set_key_active'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the token as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('set_key_active'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
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
        res = json.loads(str(response.content, encoding='utf-8'))
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
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "You are deactivating your last active key. " +
            "That is in all possible scenarios a bad idea so it will not be done."
        )

    def test_successful_activate(self):
        second_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
        second_key_object = StoredPublicKey.create(
            self.hugo,
            str(second_key.public_key().public_numbers().n),
            second_key.public_key().public_numbers().e
        )
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
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertEqual(StoredPublicKey.objects.filter(key_hash=second_key_object.key_hash).count(), 1)
        self.assertTrue(StoredPublicKey.objects.filter(key_hash=second_key_object.key_hash).all()[0].active)

    def test_successful_deactivate(self):
        second_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
        second_key_object = StoredPublicKey.create(
            self.hugo,
            str(second_key.public_key().public_numbers().n),
            second_key.public_key().public_numbers().e
        )
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
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertEqual(StoredPublicKey.objects.filter(key_hash=second_key_object.key_hash).count(), 1)
        self.assertFalse(StoredPublicKey.objects.filter(key_hash=second_key_object.key_hash).all()[0].active)


class TestDeleteKey(TestCase):
    def setUp(self):
        self.hugo = User(name='Hugo')
        self.hugo.save()
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

    def test_no_JSON(self):
        response = self.client.post(
            reverse('delete_key'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the token as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('delete_key'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
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
        res = json.loads(str(response.content, encoding='utf-8'))
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
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "You are deleting your last active key. " +
            "That is in all possible scenarios a bad idea so it will not be done."
        )

    def test_successful(self):
        second_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
        second_key_object = StoredPublicKey.create(
            self.hugo,
            str(second_key.public_key().public_numbers().n),
            second_key.public_key().public_numbers().e
        )
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
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertEqual(StoredPublicKey.objects.filter(user=self.hugo).count(), 1)
        self.assertEqual(StoredPublicKey.objects.filter(user=self.hugo).all()[0].key_hash, self.hugo_key.key_hash)


class TestRegisterNewKey(TestCase):
    def setUp(self):
        self.hugo = User(name='Hugo')
        self.hugo.save()
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

    def test_no_JSON(self):
        response = self.client.post(
            reverse('register_new_key'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the token and public_key as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('register_new_key'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token and the new public_key.")

    def test_no_public_key(self):
        response = self.client.post(
            reverse('register_new_key'),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token and the new public_key.")

    def test_wrong_session(self):
        response = self.client.post(
            reverse('register_new_key'),
            json.dumps({
                'token': 31323334,
                'public_key': {'N': '123423423', 'e': 36754}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(
            "The token could not be decoded: Ciphertext length must be equal to key size.",
            res['error']
        )

    def test_wrong_session_wrong_format(self):
        response = self.client.post(
            reverse('register_new_key'),
            json.dumps({
                'token': 3132333,
                'public_key': {'N': '123423423', 'e': 36754}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "The token is not in valid base64-format.")

    def test_public_key_in_wrong_format(self):
        response = self.client.post(
            reverse('register_new_key'),
            json.dumps({
                'token': self.authentication_token,
                'public_key': {'N': '123423423'}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
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
        res = json.loads(str(response.content, encoding='utf-8'))
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
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(
            "Factor N in the public key is too small. Please use at least 4096 bit.",
            res['error']
        )

    def test_e_not_a_number(self):
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
        response = self.client.post(
            reverse('register_new_key'),
            json.dumps({
                'token': self.authentication_token,
                'public_key': {'N': n, 'e': 'abc'}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "Factor e in the public key is not a number. It has to be a long integer.")

    def test_successful(self):
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
        e = '65537'
        response = self.client.post(
            reverse('register_new_key'),
            json.dumps({
                'token': self.authentication_token,
                'public_key': {'N': n, 'e': e}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        hasher = sha256()
        hasher.update((n + e).encode('utf-8'))
        key_hash = hasher.hexdigest()[:10]
        self.assertEqual(self.hugo.keys.filter(key_hash=key_hash).count(), 1)