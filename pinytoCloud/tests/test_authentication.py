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
import json
from unittest.mock import patch
import json

from pinytoCloud.models import User, StoredPublicKey


def mock_get_random_string(length=16):
    """
    Returns length 'a'

    @param length: int
    @return: string
    """
    return ''.join(['a' for _ in xrange(length)])


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


class TestAuthenticate(TestCase):
    def setUp(self):
        self.hugo = User(name='hugo')
        self.hugo.save()
        StoredPublicKey.create(
            self.hugo,
            "42320220477797940672783376022510199287331019358864827394693200090117085282920435294959" +
            "00957512511575892003207782616688337489994244464084583636814718532653726717087502923301" +
            "38523275693945852912768855826808731886441495500637406680770152636078902923644703441524" +
            "71716720995801406987228185438446551152555182363864496778325758261431312745814097927300" +
            "54612323112806788498516319476836390017218376332351745860926241221738209959756658009243" +
            "45638196402978881951514769899280529299457711572034383877233594083496874275349596126350" +
            "07215121155863602524811425507288611219546678112302306176224567419378498844282960279019" +
            "68169788333009960828309690454639015291151475322422098283962154573503882033352426833353" +
            "41243302167669344553957334683344937435097912351392424497312892616471741932717410139629" +
            "80063759785279475005515834241012427318321378366846873982743328829662037254303913488713" +
            "32406582311062881906761707254413153872272793345983335018763276971",
            long(65537)
        )

    def test_no_JSON(self):
        response = self.client.post(
            reverse('authenticate'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Your request contained no valid JSON data. " +
                                       "You have to supply a username and a key_hash to authenticate.")

    def test_no_token(self):
        response = self.client.post(
            reverse('authenticate'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "You have to supply a username and a key_hash to authenticate.")

    def test_unknown_user_returns_error(self):
        response = self.client.post(
            reverse('authenticate'),
            json.dumps({'username': 'Max', 'key_hash': 'wrong'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "User 'Max' is unknown. Please register first.")

    def test_wrong_hash_returns_error(self):
        response = self.client.post(
            reverse('authenticate'),
            json.dumps({'username': 'hugo', 'key_hash': 'wrong'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "This is not a registered and active public key of this user.")

    @patch('pinytoCloud.models.PKCS1_OAEP')
    @patch('pinytoCloud.views.get_random_bytes', mock_get_random_string)
    @patch('pinytoCloud.models.create_token', mock_get_random_string)
    def test_successful_response(self, cipher_mock):
        cipher_mock.new.return_value = MockCypher()
        response = self.client.post(
            reverse('authenticate'),
            json.dumps({'username': 'hugo', 'key_hash': 'b44c98daa8'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        encrypted_token = u'61616161616161616161616161616161'
        signature = u'19510491069554755379376950608707692380897304739473362067077379620777901927214268423255745186' + \
                    u'40365630465999928213643800686695349578109072043994318968544860388858746861161484963207136475' + \
                    u'93987120033443077617108441245798188146685881387281434731571459338301047625519069056124006916' + \
                    u'88242040714850951643567180701459338913497922611465363283956969336252096128673698237616276709' + \
                    u'12582000168963647412405812785986860475519146713047461951331008493899316530144442038347086925' + \
                    u'53465690223057114984145030180079312491056754119494211053137822227503653419504153189977218842' + \
                    u'03857374390902449784368746995000115125626019248435561109734956001111403918980154202848677902' + \
                    u'46969671204985429618202085253508077797305197354713259458898747090394941744286287655210722517' + \
                    u'39920674553250388195087163765781395455357883583143801994109316250182921816166246377696562385' + \
                    u'79051392498934482555166917903811748609766782106967890875660934895187954392663388462785477239' + \
                    u'52680'
        self.assertEqual(res['encrypted_token'], encrypted_token)
        self.assertEqual(res['signature'], signature)


class TestLogout(TestCase):
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
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = b16encode(pinyto_cipher.encrypt(self.session.token))

    def test_no_JSON(self):
        response = self.client.post(
            reverse('logout'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the token as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('logout'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token key.")

    def test_successful(self):
        response = self.client.post(
            reverse('logout'),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
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
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the username and public_key as JSON.")

    def test_no_username(self):
        response = self.client.post(
            reverse('register'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
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
        res = json.loads(response.content)
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
        res = json.loads(response.content)
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
        res = json.loads(response.content)
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
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "Factor N in the public key is too small. Please use at least 3072 bit."
        )

    def test_e_no_number(self):
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
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "Factor e in the public key is not a number. It has to be a long integer."
        )

    def test_successful(self):
        self.assertEqual(User.objects.filter(name='Hugo').count(), 0)
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
        e = long(65537)
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
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertEqual(User.objects.filter(name='Hugo').count(), 1)
        self.assertEqual(User.objects.filter(name='Hugo').all()[0].keys.count(), 1)
        self.assertEqual(User.objects.filter(name='Hugo').all()[0].keys.all()[0].N, n)
        self.assertEqual(User.objects.filter(name='Hugo').all()[0].keys.all()[0].e, e)