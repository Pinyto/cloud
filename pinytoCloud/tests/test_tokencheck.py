# coding=utf-8
"""
This File is part of Pinyto
"""
from django.test import TestCase
from pinytoCloud.checktoken import check_token
from pinytoCloud.models import User, StoredPublicKey, Session
from datetime import datetime
import json


class TokenCheckTest(TestCase):
    def test_no_session(self):
        response = check_token('xxx', long(123456789))
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Unknown token. Please authenticate.")

    def test_wrong_signature(self):
        hugo = User(name='hugo')
        n = "44819645633794177064374433702412067761810841911505887076937243148608168506288814968490125899991436404" + \
            "73460666964598353243015247963273818253017363770355874807104124173287768629167404409759992760226017776" + \
            "91794078550529394483028420021497231582600236168798179432868392243199461277852176728307154871958758167" + \
            "55915656270963824873414372727902912662061704317350060113171870618235070874528016637733539749452936958" + \
            "36309256427426599485862682841644121112508463341122416441266091753414530591981671500374801814002440637" + \
            "79206988072102375807281179593630496176490860308592873002017066265769227521850288496730569731325356035" + \
            "75709705804389452963429446209090281181198312212078942438375187352951092627007211829979142639030767822" + \
            "90688059670133506261782024039100227468751916576386439758688208328415660157197873568680255352172029124" + \
            "53663022693800259960461449906351642931128748448787494175277109726096069796085022115538441518684931184" + \
            "1158934104945289"
        e = long(65537)
        key = StoredPublicKey.create(hugo, n, e)
        session = hugo.start_session(key)
        response = check_token(session.token, '123456789')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "The token was found but the signature did not match. This incident was reported."
        )

    def test_successful(self):
        hugo = User(name='hugo')
        n = "44819645633794177064374433702412067761810841911505887076937243148608168506288814968490125899991436404" + \
            "73460666964598353243015247963273818253017363770355874807104124173287768629167404409759992760226017776" + \
            "91794078550529394483028420021497231582600236168798179432868392243199461277852176728307154871958758167" + \
            "55915656270963824873414372727902912662061704317350060113171870618235070874528016637733539749452936958" + \
            "36309256427426599485862682841644121112508463341122416441266091753414530591981671500374801814002440637" + \
            "79206988072102375807281179593630496176490860308592873002017066265769227521850288496730569731325356035" + \
            "75709705804389452963429446209090281181198312212078942438375187352951092627007211829979142639030767822" + \
            "90688059670133506261782024039100227468751916576386439758688208328415660157197873568680255352172029124" + \
            "53663022693800259960461449906351642931128748448787494175277109726096069796085022115538441518684931184" + \
            "1158934104945289"
        e = long(65537)
        key = StoredPublicKey.create(hugo, n, e)
        session = Session(token="abcdabcdabcdabcd", timestamp=datetime.now(), user=hugo, key=key)
        session.save()
        return_value = check_token(
            session.token,
            '23432661446612226477416271254551787803802616197457729613950923334079429998902111718395986254223804020' +
            '87945802540724391913236284083709701270741982698855911087420014063296425078946147512936749087337950359' +
            '91088622920818426244406063267686150963371520318128399928498961364706262935318442311651853788837273045' +
            '45132723998565913502670011499862385635554857093244714924988413732205544278904145177566110762609715425' +
            '38608166618133030075672849353616299035407000640012491448050867046294354747915474757290930332302915809' +
            '89676947474997090904504578756923718177410442207746084856687194063293119602429755011332701311932691907' +
            '90067065913807167782355803294472031106367847181904481331189914937821736120031005791174822800750589109' +
            '15892237993127395396943018366056201755378971970998204815582164288057915444258708411261903373211328340' +
            '38528712538458776192548248064264917474929447559690042302961587925091449241930723524979649872312480167' +
            '1630751137778521'
        )
        self.assertEqual(return_value, session)