# coding=utf-8
"""
This File is part of Pinyto
"""
from django.test import TestCase
from django.core.urlresolvers import reverse
from mock import patch
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
    def encrypt(self, message):
        """
        This does nothing.

        @param message: string
        @return: string
        """
        return message


class AuthenticateTest(TestCase):
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

    def test_unknown_user_returns_error(self):
        response = self.client.post(reverse('authenticate'), {'username': 'Max', 'keyhash': 'wrong'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "User 'Max' is unknown. Please register first.")

    def test_wrong_hash_returns_error(self):
        response = self.client.post(reverse('authenticate'), {'username': 'hugo', 'keyhash': 'wrong'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "This is not a registered public key of this user.")

    @patch('pinytoCloud.models.PKCS1_OAEP')
    @patch('database.views.get_random_bytes', mock_get_random_string)
    @patch('pinytoCloud.models.create_token', mock_get_random_string)
    def test_successful_response(self, cypher_mock):
        cypher_mock.new.return_value = MockCypher()
        response = self.client.post(
            reverse('authenticate'),
            {'username': 'hugo', 'keyhash': 'b44c98daa82c496c36727c32506df8f9bdd0e542af4b9498937d816ab28c9721'}
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