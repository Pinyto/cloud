# coding=utf-8
"""
This File is part of Pinyto
"""
from django.test import TestCase
from django.db.transaction import non_atomic_requests, commit
from pinytoCloud.models import User, StoredPublicKey
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64decode
from datetime import datetime
from django.utils import timezone


class ModelTest(TestCase):
    def test_create_user(self):
        user = User(name='hugo')
        self.assertAlmostEqual((timezone.now() - user.last_calculation_time).total_seconds(), 0.0, places=3)
        self.assertEqual(user.name, 'hugo')
        self.assertAlmostEqual(user.time_budget, 0)
        self.assertAlmostEqual(user.storage_budget, 0)
        self.assertEqual(user.current_storage, 0)
        user.save()
        self.assertEqual(User.objects.filter(name='hugo').count(), 1)

    def test_create_key(self):
        hugo = User(name='hugo')
        hugo.save()
        key = StoredPublicKey.create(hugo, '123213', 834576)
        self.assertEqual(key.key_hash, '5df78531b8')
        self.assertEqual(key.N, '123213')
        self.assertEqual(key.e, 834576)
        self.assertEqual(key.user.name, 'hugo')

    def test_start_session(self):
        hugo = User(name='hugo')
        hugo.save()
        key = StoredPublicKey.create(hugo, '123213', 834576)
        session = hugo.start_session(key)
        self.assertEqual(len(session.token), 16)
        self.assertEqual(session.user, hugo)
        self.assertEqual(session.key, key)
        self.assertEqual(hugo.sessions.count(), 1)
        self.assertEqual(key.related_session, session)

    def test_start_multiple_sessions(self):
        hugo = User(name='hugo')
        hugo.save()
        key1 = StoredPublicKey.create(hugo, '123213', 834576)
        key2 = StoredPublicKey.create(hugo, '675675', 545665)
        session1 = hugo.start_session(key1)
        session2 = hugo.start_session(key2)
        self.assertEqual(hugo.sessions.count(), 2)
        self.assertEqual(key1.related_session, session1)
        self.assertEqual(key2.related_session, session2)

    def test_overwrite_sessions(self):
        hugo = User(name='hugo')
        hugo.save()
        key = StoredPublicKey.create(hugo, '123213', 834576)
        session = hugo.start_session(key)
        old_token = session.token
        session = hugo.start_session(key)
        self.assertNotEqual(session.token, old_token)
        self.assertEqual(hugo.sessions.count(), 1)

    def test_multiple_users_multiple_sessions(self):
        hugo = User(name='hugo')
        hugo.save()
        willi = User(name='willi')
        willi.save()
        karl = User(name='karl')
        karl.save()
        hugo_key1 = StoredPublicKey.create(hugo, '123213', 834576)
        hugo_key2 = StoredPublicKey.create(hugo, '675675', 545665)
        willi_key = StoredPublicKey.create(hugo, '479836', 196893)
        karl_key1 = StoredPublicKey.create(hugo, '248566', 315485)
        karl_key2 = StoredPublicKey.create(hugo, '942552', 781356)
        hugo_session1 = hugo.start_session(hugo_key1)
        self.assertEqual(hugo.sessions.count(), 1)
        willi_session = willi.start_session(willi_key)
        karl_session1 = karl.start_session(karl_key1)
        karl_session2 = karl.start_session(karl_key2)
        self.assertEqual(willi.sessions.count(), 1)
        self.assertEqual(karl.sessions.count(), 2)
        hugo_session2 = hugo.start_session(hugo_key2)
        self.assertEqual(hugo.sessions.count(), 2)
        self.assertNotEqual(hugo_session1.token, hugo_session2.token)
        self.assertNotEqual(hugo_session1.token, willi_session.token)
        self.assertNotEqual(hugo_session2.token, willi_session.token)
        self.assertNotEqual(karl_session1.token, karl_session2.token)
        self.assertNotEqual(karl_session1.token, hugo_session1.token)

    def test_get_encrypted_token(self):
        hugo = User(name='hugo')
        hugo.save()
        key = StoredPublicKey.create(
            hugo,
            '425459331484582537015228348890619636855413475085489045693909215308544091998991169014958758605127751846' +
            '006675827510313643957363733495040060163148245516866504721450324530867669011501594156260170954794195671' +
            '248440166115134306603838661277715020350031810275579151793293609594804675283243365619966947743955136368' +
            '906902997378815701054835807736041597739581656990863424321613011857882988095753224735812197778217423885' +
            '841237678749745004064640051566000713671312390059529468581814000689381368262635236252902925794779198035' +
            '440541233967232815314707387583630453661487169126476480662608321726354981733021424535666350363091585596' +
            '773509890553520647739778537073744646301718153394252974338493323330467752730038537907555683045977517145' +
            '123643303950276393220303004639969615396630485823420591373138524480778223744937045683437364751850606773' +
            '020916979709818469855115771522472889917358007025437544275329719658313372687629568527255894518417396349' +
            '5164173', 65537)
        session = hugo.start_session(key)
        encrypted_token = session.get_encrypted_token()
        private_key = RSA.construct((int(
            '425459331484582537015228348890619636855413475085489045693909215308544091998991169014958758605127751846' +
            '006675827510313643957363733495040060163148245516866504721450324530867669011501594156260170954794195671' +
            '248440166115134306603838661277715020350031810275579151793293609594804675283243365619966947743955136368' +
            '906902997378815701054835807736041597739581656990863424321613011857882988095753224735812197778217423885' +
            '841237678749745004064640051566000713671312390059529468581814000689381368262635236252902925794779198035' +
            '440541233967232815314707387583630453661487169126476480662608321726354981733021424535666350363091585596' +
            '773509890553520647739778537073744646301718153394252974338493323330467752730038537907555683045977517145' +
            '123643303950276393220303004639969615396630485823420591373138524480778223744937045683437364751850606773' +
            '020916979709818469855115771522472889917358007025437544275329719658313372687629568527255894518417396349' +
            '5164173'), 65537, int(
            '143951282730963168527330720177923918208522489533326732978573064684859799746488703812162526714834410629' +
            '619177408169639970415346802974182801990595376597814942333238315701778532625250413488882814757337175867' +
            '285089525663930117561583814870562474041253114439945254007118002031756089990854607157134856634793493657' +
            '691711049695253968829667656449623668893563691687373629719203609029047673497951264252130852396877994983' +
            '667906744107860379940023627926583454002283914997329850726851006872297055289709641358683935846980675389' +
            '267233162339007879173769742566321115017576506039352457168615505674126638435635681103572222392049743237' +
            '832716765927447810212302709881441414529952515894753254726828768444192167591747783721049589172316115578' +
            '777463229698631227717061023753056782517333576196556812627813200296010566580463445753423064585712280961' +
            '168635394371010171274723398773491820477253625411439437269468866624580286294641090126678140483576730725' +
            '3639169'
        )))
        cipher = PKCS1_OAEP.new(private_key)
        self.assertEqual(session.token, str(cipher.decrypt(b64decode(encrypted_token)), encoding='utf-8'))

    def test_budget_update(self):
        hugo = User(name='hugo')
        hugo.save()
        hugo.calculate_time_and_storage(1000, 30000)
        time1 = timezone.now()
        self.assertAlmostEqual((time1 - hugo.last_calculation_time).total_seconds(), 0.0, places=2)
        self.assertAlmostEqual(hugo.time_budget, 1000)
        self.assertAlmostEqual(hugo.storage_budget, 0.0)
        self.assertEqual(hugo.current_storage, 30000)
        self.assertEqual(User.objects.filter(name='hugo').count(), 1)
        self.assertEqual(User.objects.filter(name='hugo').all()[0].current_storage, 30000)
        hugo.calculate_time_and_storage(1100, 0)
        time2 = timezone.now()
        self.assertAlmostEqual((time2 - hugo.last_calculation_time).total_seconds(), 0.0, places=2)
        self.assertAlmostEqual(hugo.time_budget, 2100)
        self.assertAlmostEqual(hugo.storage_budget, (time2 - time1).total_seconds() * 30000, places=-2)
        self.assertEqual(hugo.current_storage, 0)