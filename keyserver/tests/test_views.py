# coding=utf-8
"""
This File is part of Pinyto
"""

import json
import mock
from django.core.urlresolvers import reverse
from django.test import TestCase
from unittest import skip
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

    def test_missing_account_returns_error(self):
        response = self.client.post(reverse('authenticate'), {'name': 'Max', 'password': '123a'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Max is not a valid account name. Authentication failed.")

    def test_wrong_password_returns_error(self):
        response = self.client.post(reverse('authenticate'), {'name': 'Hugo', 'password': '123a'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Wrong password. Authentication failed.")

    def mock_wrong_signature_cloud_authenticate(self, param):
        return {'encrypted_token': '48616C6C6F2057656C7421',
                'signature': '23456789348578923589293576897'}

    @mock.patch('keyserver.views.cloud_authenticate', mock_wrong_signature_cloud_authenticate)
    def test_wrong_signature_pinyto_cloud_returns_error(self):
        response = self.client.post(reverse('authenticate'), {'name': 'Hugo', 'password': 'b123'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Pinyto-Cloud signature is wrong. This is a man-in-the-middle-attack! " +
                                       "The developers will be informed. Authentication aborted.")

    def mock_cloud_authenticate(self, param):
        return {
            'encrypted_token': '2F78453236DBB543B240B897CD7C1D1B58777B1FD536E88BF8FC33B5FB46EA78DCC601B8AF9FD' + \
                               '88D13A50996C4B29EE37671BFED3FD66C0E93B1FA43F4C4442B703B240E120A5C56C624F0F10D' + \
                               '45A4DC39B0EF0706023E4A279C369232FE185B104FD42C4F39B437B82497BFD21534B2EF0BBAD' + \
                               '6E1D33CCF25F5002F82144145100E8C66B28D62CAF24441A2AAED01550B94B2675A62061DC037' + \
                               'C31930D7C1FD79740699CC79CCA2CF1530F1BECD5B9E0D531E0A284D622689E895FFFFDC708C5' + \
                               '9946C576C94AFFF5235748A267015F01E30D51FF02EBDF29A21B3CB5D3A556D596DD43E964DFB' + \
                               '3D3F6E15FCA4EF1B6725EFABF25EBA016B5937A825C1AF16DDEB707E20AB463C19FED8C21FC05' + \
                               '19C31793B04BEDB5652ED3ABAD49A077080E0D5E1F0D0DCB1215637D958C9077E0F71EFE06195' + \
                               '26C05994480B5FF7A333ACCAE93AD402C35F77848D7937279ADAA931E885005F96D4BDA6F903D' + \
                               'C7748497D7EC59209AEFFF245CFB5767F2485EBEBF87F1FA49ACE54AC676E83DA32D9A13473',
            'signature':
                '290253272399975850626178062509445415393683240869208995537567532936434175352728979019' + \
                '31383101748938197010526062905450939343036284540623707339418124634085649393121564786810133329726168' + \
                '74410593315670558626613729531454111175578424501163677325862728190950424163247693358965366870106656' + \
                '73928611864992744515778345907236459846802330926995641218238438872786836583139578748136246954513127' + \
                '43540582475779546485917118376886765622179591081551227790932017717432104905042760343424687678139071' + \
                '69317246461047771129420756922151668384220232525570023301989097684368494865897097153262825967843297' + \
                '87949024765709323679347463529906738973533580782084110648023864364802801389382706134156435359679781' + \
                '01850022889290541487134288708973595109900228276531873416519372661710902711063931609988022436708966' + \
                '15766749289464748350827810894521557325435340811696825722024470238235575070191152788666547261010494' + \
                '586454893834564736984828076584996698178733674599088504406'}

    @mock.patch('keyserver.views.PKCS1_OAEP')
    @mock.patch('keyserver.views.cloud_authenticate', mock_cloud_authenticate)
    def test_authentication_successful(self, cipher_mock):
        cipher_mock.new.return_value = MockCypher()
        # set the key of hugo to a one which we know
        self.hugo.N = long("42320220477797940672783376022510199287331019358864827394693200090117085282920435294959" +
                           "00957512511575892003207782616688337489994244464084583636814718532653726717087502923301" +
                           "38523275693945852912768855826808731886441495500637406680770152636078902923644703441524" +
                           "71716720995801406987228185438446551152555182363864496778325758261431312745814097927300" +
                           "54612323112806788498516319476836390017218376332351745860926241221738209959756658009243" +
                           "45638196402978881951514769899280529299457711572034383877233594083496874275349596126350" +
                           "07215121155863602524811425507288611219546678112302306176224567419378498844282960279019" +
                           "68169788333009960828309690454639015291151475322422098283962154573503882033352426833353" +
                           "41243302167669344553957334683344937435097912351392424497312892616471741932717410139629" +
                           "80063759785279475005515834241012427318321378366846873982743328829662037254303913488713" +
                           "32406582311062881906761707254413153872272793345983335018763276971")
        self.hugo.e = long(65537)
        self.hugo.d = long("10989296307294587093846643776051369020122973090760358768373420802502594829557959135291" +
                           "70430366783984596946924486085277051549578437406194843284424262324926394575146789214470" +
                           "34459757171667463034156284060311442379777245989743921554135014687287955963113745871307" +
                           "31703849091452894458224350516372177663215955772590231566497516732426538906392790614870" +
                           "99949532550067075494266608554813337279903296281855471124116800785991742940554782886023" +
                           "24092815148479402674075382671558799161961879631551267479682749265619265947459983940265" +
                           "88476234200494375037153156395490897112126615060451460585042141868371909906413121103800" +
                           "32558056801121539728171424903777453462747380518086642347607502129848324882186479469980" +
                           "23720986776522488114566069969274378757418711462197964528276101882252047638876935011334" +
                           "61943536058172250284493872241602927081466173228570347358923898232778648464146232798951" +
                           "76897011486238041195423698137185180296903854366288149786346385889")
        self.hugo.save()
        key_data = {'N': unicode(self.hugo.N), 'e': unicode(self.hugo.e)}
        cloud_register('Hugo', key_data)
        # do the response
        response = self.client.post(reverse('authenticate'), {'name': 'Hugo', 'password': 'b123'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertIn('token', res)
        token = u'2F78453236DBB543B240B897CD7C1D1B58777B1FD536E88BF8FC33B5FB46EA78DCC601B8AF9FD88D13A50996C4B29EE' + \
                u'37671BFED3FD66C0E93B1FA43F4C4442B703B240E120A5C56C624F0F10D45A4DC39B0EF0706023E4A279C369232FE18' + \
                u'5B104FD42C4F39B437B82497BFD21534B2EF0BBAD6E1D33CCF25F5002F82144145100E8C66B28D62CAF24441A2AAED0' + \
                u'1550B94B2675A62061DC037C31930D7C1FD79740699CC79CCA2CF1530F1BECD5B9E0D531E0A284D622689E895FFFFDC' + \
                u'708C59946C576C94AFFF5235748A267015F01E30D51FF02EBDF29A21B3CB5D3A556D596DD43E964DFB3D3F6E15FCA4E' + \
                u'F1B6725EFABF25EBA016B5937A825C1AF16DDEB707E20AB463C19FED8C21FC0519C31793B04BEDB5652ED3ABAD49A07' + \
                u'7080E0D5E1F0D0DCB1215637D958C9077E0F71EFE0619526C05994480B5FF7A333ACCAE93AD402C35F77848D7937279' + \
                u'ADAA931E885005F96D4BDA6F903DC7748497D7EC59209AEFFF245CFB5767F2485EBEBF87F1FA49ACE54AC676E83DA32' + \
                u'D9A13473'
        self.assertEqual(res['token'], token)

    def test_authentication_real_request(self):
        jonny = Account.create(u'jonny', u'1234', 2)
        key_data = {'N': unicode(jonny.N), 'e': unicode(jonny.e)}
        cloud_register('jonny', key_data)
        response = self.client.post(reverse('authenticate'), {'name': 'jonny', 'password': '1234'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertIn('token', res)
        self.assertTrue(len(res['token']) > 10)

    def mock_cloud_register_success(self, param):
        return {'success': True}

    @mock.patch('keyserver.views.cloud_register', mock_cloud_register_success)
    def test_register_successful(self):
        response = self.client.post(reverse('register'), {'name': 'Jaal', 'password': 'abc'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertEqual(Account.objects.filter(name='Jaal').count(), 1)
        created_account = Account.objects.filter(name='Jaal').all()[0]
        hash_string = 'abc' + created_account.salt
        for i in range(created_account.hash_iterations):
            hasher = sha256()
            hasher.update(hash_string)
            hash_string = hasher.hexdigest()
        self.assertEqual(created_account.hash, hash_string)
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])

    def test_register_successful_real_request(self):
        response = self.client.post(reverse('register'), {'name': 'jonny', 'password': '1234'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertEqual(Account.objects.filter(name='jonny').count(), 1)
        created_account = Account.objects.filter(name='jonny').all()[0]
        hash_string = u'1234' + created_account.salt
        for i in range(created_account.hash_iterations):
            hasher = sha256()
            hasher.update(hash_string)
            hash_string = hasher.hexdigest()
        self.assertEqual(created_account.hash, hash_string)
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])