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
            json.dumps({'username': 'hugo', 'public_key': {'N': str(pow(2, 4096) - 7458345), 'e': 'xxx'}}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual("Factor e in the public key is not a number. It has to be an integer.", res['error'])

    def test_n_too_small(self):
        response = self.client.post(
            '/register',
            json.dumps({'username': 'hugo', 'public_key': {"N": 3845, "e": 1}}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual("Factor N in the public key is too small. Please use at least 4096 bit.", res['error'])

    def test_successful_registration(self):
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
        self.assertEqual(key.public_numbers().n, int(n))
        self.assertEqual(key.public_numbers().e, int(e))

    def test_successful_registration_Klaus_Merkert(self):
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
        self.assertEqual(key.public_numbers().n, int(n))
        self.assertEqual(key.public_numbers().e, int(e))