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

import json
from unittest import mock
from django.urls import reverse
from django.test import TestCase
from base64 import b64decode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from pinytoCloud.settings import PINYTO_KEY
from hashlib import sha256
from keyserver.models import Account
from pinytoCloud.views import register as cloud_register


class MockCypher(object):
    """
    This class mocks Crypto.Cipher objects and does nothing.
    """
    @staticmethod
    def encrypt(message):
        """
        This does nothing.

        @param message: string
        @return: string
        """
        return message

    @staticmethod
    def decrypt(message):
        """
        This does nothing.

        @param message: string
        @return: string
        """
        return message


class KeyserverTest(TestCase):
    def setUp(self):
        self.hugo = Account.create(u'Hugo', u'b123', 2)

    def test_no_name(self):
        response = self.client.post(
            reverse('keyserver_authenticate'),
            json.dumps({'password': '123a'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "Please supply username and password in the JSON request data. Authentication failed.")

    def test_missing_account_returns_error(self):
        response = self.client.post(
            reverse('keyserver_authenticate'),
            json.dumps({'name': 'Max', 'password': '123a'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Max is not a valid account name. Authentication failed.")

    def test_wrong_password_returns_error(self):
        response = self.client.post(
            reverse('keyserver_authenticate'),
            json.dumps({'name': 'Hugo', 'password': '123a'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 403)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Wrong password. Authentication failed.")

    def mock_wrong_signature_cloud_authenticate(self, param):
        return {'encrypted_token': 'dGVzdA==',
                'signature': 'Rm9v'}

    @mock.patch('keyserver.views.cloud_authenticate', mock_wrong_signature_cloud_authenticate)
    def test_wrong_signature_pinyto_cloud_returns_error(self):
        response = self.client.post(
            reverse('keyserver_authenticate'),
            json.dumps({'name': 'Hugo', 'password': 'b123'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 403)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Pinyto-Cloud signature is wrong. This is a man-in-the-middle-attack! " +
                                       "The developers will be informed. Authentication aborted.")

    def mock_cloud_authenticate(self, param):
        return {
            'encrypted_token':
                'MzeTM7A8cJzycR0tBx1MqcPlZkUzD88YcVQCfJl8Eq5wu8gOALuH0OZ0jSKdKYjpuf2g85SNdf5WV4vvCzTLBZcN6wcLC7ID' +
                '0V1qY+MqanztEVmAAUswqR1Ksf8TSJap7B+EpCtzlTsYif05nP68byxEsbL5sti3WMbnbjo3y5+aFN5x+CFEXuVwCUzJXTEF' +
                '7Ui48aShf6+sr5E3BCtrrj0DQDrhiiLYfHGNleNN9X1nQ+GRZaTlB7XO8nYw6SyUbopA1Bj9flPBrFICGIvTIfD1S+gMzqL2' +
                'oWo5m9EoCSLACyFQiYEnsoHl1vMlDPrOwz2N9GWPIi/5VqRlSNrLcyiMNQmPRMZM22kxUTsH0m7omHcEurnJGjHQyubPGGiu' +
                'Kew0H5vLgAIGxo7M2D2inGduWmSyO1aZR1C3x0VIKIo+VyY3qEFvi5eSKLlNFr2sDW52v19qek+QGuSEzGjN4tNA6HkxajLJ' +
                '7pwt7aqmwXJWGSSqlsBYMa6QLSmloavVzxGFo/82c+zRobdQkYpWIbVsCmJ7AO4kP9yAdlq4rQmS0c6C70N7r8yOt1ZhIKpR' +
                'IfkZx6ukWaduuVdFNVguPeoYXr3GjPjy7tQf5D23pFpksPzR4EKwSYozfglim0PrGMVaVpWF/kO+3kK9J4XTyAUoEXin5lM/' +
                'pyRkgaUyEUo=',
            'signature':
                'Dya3LrneNDKBEwYF0bo98tKYeCRrmWptCFJZ7ZHlr6xFYIpKc7KO0HVQuckEnZ7lHIjDfw3o0Y73eVInBZz6HFZlWzElI4Nc' +
                'PJjRUFSCm040okLGqhYOO3sgO0F7/DvkauisXoaASbf5mkr2EaTpiQoktQwl7EwwuPLP2sm9PLY86153q4YITOhDqerFK2s2' +
                'P/FKAv2+U2fqZcGzvXc5wF8NmGQb1DwbP+uQR+iZUlRYkOlaeo7h5Ph4Z8u2KxckTV2kswRxF6Aimux44aNHdsrLH0sLJlkQ' +
                'dLVwznCW6T8Ni3qw2siDwYvrFMxUvL8pooP4agcxmTjhnrqUUdF/XaN6wy761XbwuoIginc3cjgmoRjXSlASg9gznFwRqZ27' +
                '6Hjba0FMEYRcnHNVjg90Fl9/nE12LGnWMGEdfTCrvsNEKBRgQKJBEInWtOqHWgEv/hIPY5BN47BiB38doZ8mR0i1xO7/xHrk' +
                'YbfapLUfazc4CCWgTQ5msA8RmvH+FeUMOkSp3XmJDVh+9CrT6+NStfNf+mMZ5WYYhuCoIKYVAesstgXdOtd9mUtd8s3Q8vXb' +
                'LOfO5zISumnrSEWGODeIvQh8BD9n+lSn/t/66f/HV15rHkCpgyN3V2VFDPUlIk+hnXQetmoILYzdcrvdatj/Qj7e/F46XOXz' +
                '9nnl9/su0W4='}

    @mock.patch('keyserver.views.cloud_authenticate', mock_cloud_authenticate)
    def test_authentication_successful(self):
        # set the key of hugo to a one which we know
        self.hugo.N = "807868342350444606697534119379344654492778423715203552754482688093090898371032757342761202" + \
                      "620618438204095305716081475644326482842070819666778591402675849255593679903699387320384533" + \
                      "328397129198887564905333027288001767527397028650823278786089145167250771444492046507010295" + \
                      "794694133677261621634734055301258662979395580909393355155636367965473326849807639466278419" + \
                      "089976743288205779417024622242959102308014121410665067514495302708343511056493822082092872" + \
                      "300812458054212217229678337694559458100294489203359057842535940573304150410796515106223801" + \
                      "062333873813388035169746762875303718505405319147637352283378474967975853718992741242663658" + \
                      "930592616291734571847674776623771203239701032856330027290630661091600120928250742376280598" + \
                      "390183949229740927807387255612102751868189650876792672532605069017999797844603729682647239" + \
                      "404910676547202128069245677198953319406711723439170624972901903301563069197612866520394323" + \
                      "835850885389999581997544248800857769634558374932759292220014161412475085862281292510429868" + \
                      "997724164938862799128494322575531123456508749268306347068030782446662049588475559234968890" + \
                      "514758626359418505446346340443066573322965964230819589016760515701110073871142950630314224" + \
                      "844688783674908255012477718172292636924864748621071981918534901"
        self.hugo.e = 65537
        self.hugo.d = "360981072331513799266530191371358604485504728017395072079318110962022580647532283534879824" + \
                      "489100665950054578827070661348069895227843842152096438204921793332023213181865707284284307" + \
                      "703873865624917580156061039887419988102480958649476004333000206403676878572112014433240604" + \
                      "575305903697223390267353587674780027872631035771406610195426330157024595319739489359148225" + \
                      "042813661755219464492548469380087803103405488981642672644376160710913398199160246667561952" + \
                      "369760471514710019826264559577757284755314155695731672945982002284948025399846882652099696" + \
                      "206866123880422589100979053115650610993977285593167405042440991515666034458478628977279502" + \
                      "985212030307216106758712166312579128544507734759003289210611219745934405274223897084561822" + \
                      "137932399083142583918740372397502460510120594954159136340171379577493453659410221849860581" + \
                      "593154670567309007488277263514444792450770300449810192042421328230977292178860230261700763" + \
                      "685669270770501405675034351618909669370007280676442220640991260037826166141526852227371396" + \
                      "460079255842102479788906257161507170127528789232193142668697974172510461672383737688051787" + \
                      "992466496566766079395368328814984191056646550477157522789517183162605644734290865079120007" + \
                      "599484103339788186676097316689224435074954731141507480179239297"
        self.hugo.p = "306764779410819004604837283026466549232179699925882732977367107605627708677272423247278646" + \
                      "253097632023698319747328548756633974406294589644174057612524991732992142751728501087454631" + \
                      "252489892847152514230321239505890918485372045977851903581969036811422311569856208155935196" + \
                      "367298194734566451701125459443649176840659499661434337449416655863302554962632220239409341" + \
                      "902995626303894354667720456842831606505249104579570636714890126392817926464389954569080584" + \
                      "072334156344979077180940427291690670945072592010535916892280187122947775780242839333699083" + \
                      "08413731672214194629426190670142365361212272623355702487312097988906233036617"
        self.hugo.q = "263351074364553547516917000245358796208646356288284815855317383573840322671167310776359793" + \
                      "196156744452502269130943043859746174835819714992566570816755422578339683158371810658757499" + \
                      "811541882978835350414743314017089077609216175569970340651376344100347194745110329685247994" + \
                      "771983502487271255357448941047108742623716895583724956444961789338616316178773907307020098" + \
                      "678911029272213391931192241486628765465235360711376861081843128231234956254603292334803286" + \
                      "268213506193936430234313231041517960577966605893645175270784255524325038803594363104924155" + \
                      "31558320227588506657169238790141393483469297371036395601442300265983467672653"
        self.hugo.save()
        key_data = {'N': str(self.hugo.N), 'e': self.hugo.e}
        cloud_register('Hugo', key_data)
        # do the response
        response = self.client.post(
            reverse('keyserver_authenticate'),
            json.dumps({'name': 'Hugo', 'password': 'b123'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('token', res)
        token = PINYTO_KEY.decrypt(
            b64decode(res['token'].encode('utf-8')),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None)
        )
        self.assertEqual(token, b'f49b8f95942e0756')

    def test_authentication_real_request(self):
        jonny = Account.create('jonny', '1234', 2)
        key_data = {'N': str(jonny.N), 'e': str(jonny.e)}
        cloud_register('jonny', key_data)
        response = self.client.post(
            reverse('keyserver_authenticate'),
            json.dumps({'name': 'jonny', 'password': '1234'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('token', res)
        self.assertTrue(len(res['token']) > 10)

    def test_authentication_real_request_Klaus_Merkert(self):
        jonny = Account.create('KlausMerkert', '2P4#a$w7/9P2', 2)
        key_data = {'N': str(jonny.N), 'e': str(jonny.e)}
        cloud_register('KlausMerkert', key_data)
        response = self.client.post(
            reverse('keyserver_authenticate'),
            json.dumps({'name': 'KlausMerkert', 'password': '2P4#a$w7/9P2'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertNotIn('error', res)
        self.assertIn('token', res)
        self.assertTrue(len(res['token']) > 10)

    def mock_cloud_register_success(self, param):
        return {'success': True}

    @mock.patch('keyserver.views.cloud_register', mock_cloud_register_success)
    def test_register_successful(self):
        response = self.client.post(
            reverse('keyserver_register'),
            json.dumps({'name': 'Jaal', 'password': 'abc'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertEqual(Account.objects.filter(name='Jaal').count(), 1)
        created_account = Account.objects.filter(name='Jaal').all()[0]
        hash_string = 'abc' + created_account.salt
        for i in range(created_account.hash_iterations):
            hasher = sha256()
            hasher.update(hash_string.encode('utf-8'))
            hash_string = hasher.hexdigest()
        self.assertEqual(created_account.hash, hash_string)
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])

    def test_register_successful_real_request(self):
        response = self.client.post(
            reverse('keyserver_register'),
            json.dumps({'name': 'jonny', 'password': '1234'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertEqual(Account.objects.filter(name='jonny').count(), 1)
        created_account = Account.objects.filter(name='jonny').all()[0]
        hash_string = '1234' + created_account.salt
        for i in range(created_account.hash_iterations):
            hasher = sha256()
            hasher.update(hash_string.encode('utf-8'))
            hash_string = hasher.hexdigest()
        self.assertEqual(created_account.hash, hash_string)
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])

    def test_register_successful_real_request_Klaus_Merkert(self):
        response = self.client.post(
            reverse('keyserver_register'),
            json.dumps({'name': 'KlausMerkert', 'password': '123456'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertEqual(Account.objects.filter(name='KlausMerkert').count(), 1)
        created_account = Account.objects.filter(name='KlausMerkert').all()[0]
        hash_string = u'123456' + created_account.salt
        for i in range(created_account.hash_iterations):
            hasher = sha256()
            hasher.update(hash_string.encode('utf-8'))
            hash_string = hasher.hexdigest()
        self.assertEqual(created_account.hash, hash_string)
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
