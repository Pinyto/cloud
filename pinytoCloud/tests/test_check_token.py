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
from pinytoCloud.checktoken import check_token
from pinytoCloud.models import User, StoredPublicKey, Session
from django.utils import timezone
from base64 import b64encode
from pinytoCloud.settings import PINYTO_KEY
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import json


class TokenCheckTest(TestCase):
    def test_no_base16_token(self):
        response = check_token('xxx')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "The token is not in valid base64-format.")

    def test_wrong_length(self):
        response = check_token(
            '6385AAC2648396659A7CFD4D0599034F847C4ACD1F9F90BCE6C58D4F79069B5ACA68C81664C1184DF592DD1C4C62C63F01DE9' +
            '14CF5A00750312BA6F87D13F2DD872EACD7CB23D768E4905A6294FC79D793803A9D105ECC278A3E57339943E45FF970D7DACA' +
            '74150B269ACDB1ED4A6593B75885A7D59788DE17D6E33C92473E6A3DC59B1A5256F9CDDAD635E65CB502F41C78A7E8890BEC4' +
            '4DD4A5E837D01982E99FED24F6621E76972F140AAF9EE4B5938BA2FFB967AA08B4F6E8E76DAB6A87B967EE129D33CA7FE76EF' +
            'A40DDC1F1D74D836083BD10FF85BFC8CFCB7FF552C290D178A102A2AC39E511F9DE66CE8D666A002D29334ED9CF3CB7FFB5B1' +
            'DF68A09945B7750A90BA4CF37300A97F2C80BA5F91D2D053A78302395514B5D08A4E7F1758641F55C4D64ECFB50BB9202EE48' +
            'A93BE55C1FB7355461B973A24E1961FDE235CA7E02CE58F90D0C75A044D327A69462ED1027DC793276E91C2FB776A7A78406E' +
            'A798D01899BD166BA61D9A33DE7FA32E1898BAC6F306D1DDAC1DCEA1400E8AAAA'
        )
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(
            "The token could not be decoded: Ciphertext length must be equal to key size.",
            res['error']
        )

    def test_no_session(self):
        authentication_token = str(b64encode(PINYTO_KEY.public_key().encrypt(
            b'not really a valid token',
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None)
        )), encoding='utf-8')
        response = check_token(authentication_token)
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual("Unknown token. Please authenticate.", res['error'])

    def test_successful(self):
        hugo = User(name='hugo')
        hugo.save()
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
        e = 65537
        key = StoredPublicKey.create(hugo, n, e)
        session = Session(token="abcdabcdabcdabcd", timestamp=timezone.now(), user=hugo, key=key)
        session.save()
        authentication_token = str(b64encode(PINYTO_KEY.public_key().encrypt(
            session.token.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None)
        )), encoding='utf-8')
        return_value = check_token(authentication_token)
        self.assertIsInstance(return_value, Session)
        self.assertEqual(return_value, session)
