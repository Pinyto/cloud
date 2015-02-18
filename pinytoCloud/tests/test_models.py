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
from django.db.transaction import non_atomic_requests, commit
from pinytoCloud.models import User, StoredPublicKey
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
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
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
        public_key = private_key.public_key()
        key = StoredPublicKey.create(
            hugo,
            str(public_key.public_numbers().n),
            public_key.public_numbers().e)
        session = hugo.start_session(key)
        encrypted_token = session.get_encrypted_token()
        token = private_key.decrypt(
            b64decode(encrypted_token.encode('utf-8')),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None)
        )
        self.assertEqual(session.token, str(token, encoding='utf-8'))

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