# coding=utf-8
"""
This File is part of Pinyto
"""
from django.test import TestCase
from django.core.urlresolvers import reverse
import json

from pinytoCloud.models import User, StoredPublicKey


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