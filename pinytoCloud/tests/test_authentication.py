# coding=utf-8
"""
Pinyto cloud - A secure cloud database for your personal data
Copyright (C) 2105 Johannes Merkert <jonny@pinyto.de>

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
from django.core.urlresolvers import reverse
from django.utils import timezone
from pinytoCloud.models import User, StoredPublicKey
from keyserver.settings import PINYTO_PUBLIC_KEY
from base64 import b64encode, b64decode
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from pinytoCloud.settings import PINYTO_KEY
import json

from pinytoCloud.models import User, StoredPublicKey


class TestAuthenticate(TestCase):
    def setUp(self):
        self.hugo = User(name='hugo')
        self.hugo.save()
        self.hugo_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
        self.stored_key_hugo = StoredPublicKey.create(
            self.hugo,
            str(self.hugo_key.public_key().public_numbers().n),
            self.hugo_key.public_key().public_numbers().e
        )

    def test_no_JSON(self):
        response = self.client.post(
            reverse('authenticate'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Your request contained no valid JSON data. " +
                                       "You have to supply a username and a key_hash to authenticate.")

    def test_no_token(self):
        response = self.client.post(
            reverse('authenticate'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "You have to supply a username and a key_hash to authenticate.")

    def test_unknown_user_returns_error(self):
        response = self.client.post(
            reverse('authenticate'),
            json.dumps({'username': 'Max', 'key_hash': 'wrong'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "User 'Max' is unknown. Please register first.")

    def test_wrong_hash_returns_error(self):
        response = self.client.post(
            reverse('authenticate'),
            json.dumps({'username': 'hugo', 'key_hash': 'wrong'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "This is not a registered and active public key of this user.")

    def test_successful_response(self):
        response = self.client.post(
            reverse('authenticate'),
            json.dumps({'username': 'hugo', 'key_hash': self.stored_key_hugo.key_hash}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('encrypted_token', res)
        token = str(self.hugo_key.decrypt(
            b64decode(res['encrypted_token'].encode('utf-8')),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None)
        ), encoding='utf-8')
        self.assertEqual(self.hugo.sessions.all()[0].token, token)
        signature = b64decode(res['signature'])
        verifier = PINYTO_PUBLIC_KEY.verifier(
            signature,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        verifier.update(res['encrypted_token'].encode('utf-8'))
        verifier.verify()


class TestLogout(TestCase):
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
        key = StoredPublicKey.create(self.hugo, n, int(65537))
        self.session = self.hugo.start_session(key)
        self.authentication_token = str(b64encode(PINYTO_PUBLIC_KEY.encrypt(
            self.session.token.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None)
        )), encoding='utf-8')

    def test_no_JSON(self):
        response = self.client.post(
            reverse('logout'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the token as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('logout'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token key.")

    def test_successful(self):
        response = self.client.post(
            reverse('logout'),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertEqual(self.hugo.sessions.count(), 0)


class TestRegister(TestCase):
    def test_no_JSON(self):
        response = self.client.post(
            reverse('register'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the username and public_key as JSON.")

    def test_no_username(self):
        response = self.client.post(
            reverse('register'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with username and public_key.")

    def test_username_already_taken(self):
        self.hugo = User(name='Hugo')
        self.hugo.save()
        response = self.client.post(
            reverse('register'),
            json.dumps({
                'username': 'Hugo',
                'public_key': 'fake'
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Username Hugo is already taken. Try another username.")

    def test_key_wrong_format(self):
        response = self.client.post(
            reverse('register'),
            json.dumps({
                'username': 'Hugo',
                'public_key': {
                    'N': '123'
                }
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "The public_key is in the wrong format. The key data must consist of an N and an e."
        )

    def test_N_no_number(self):
        response = self.client.post(
            reverse('register'),
            json.dumps({
                'username': 'Hugo',
                'public_key': {
                    'N': 'foo',
                    'e': 1234
                }
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "Factor N in the public key is not a number. It has to be a long integer transferred as a string."
        )

    def test_small_N(self):
        response = self.client.post(
            reverse('register'),
            json.dumps({
                'username': 'Hugo',
                'public_key': {
                    'N': '123',
                    'e': 1234
                }
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(
            "Factor N in the public key is too small. Please use at least 4096 bit.",
            res['error']
        )

    def test_e_no_number(self):
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
            reverse('register'),
            json.dumps({
                'username': 'Hugo',
                'public_key': {
                    'N': n,
                    'e': 'bar'
                }
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(
            "Factor e in the public key is not a number. It has to be an integer.",
            res['error']
        )

    def test_successful(self):
        self.assertEqual(User.objects.filter(name='Hugo').count(), 0)
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
        e = int(65537)
        response = self.client.post(
            reverse('register'),
            json.dumps({
                'username': 'Hugo',
                'public_key': {
                    'N': n,
                    'e': e
                }
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertEqual(User.objects.filter(name='Hugo').count(), 1)
        self.assertEqual(User.objects.filter(name='Hugo').all()[0].keys.count(), 1)
        self.assertEqual(User.objects.filter(name='Hugo').all()[0].keys.all()[0].N, n)
        self.assertEqual(User.objects.filter(name='Hugo').all()[0].keys.all()[0].e, e)