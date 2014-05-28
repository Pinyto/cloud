# coding=utf-8
"""
This File is part of Pinyto
"""
from django.test import TestCase
from pinytoCloud.models import User, StoredPublicKey


class ModelTest(TestCase):
    def test_create_user(self):
        user = User(name='hugo')
        self.assertEqual(user.name, 'hugo')
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
