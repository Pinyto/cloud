# coding=utf-8
"""
In this file is the model definition for Pinyto users and for sessions.
"""

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b16encode
from hashlib import sha256
from datetime import datetime
import random


class User(models.Model):
    """
    This is an user object. Users have a username and a list of public keys
    for authentication.
    """
    name = models.CharField(max_length=30, primary_key=True)

    def start_session(self):
        """
        Creates a session object with a new random token.
        If there is an existing session it will be overwritten

        @return: User object
        """
        ru = lambda: unichr(random.randint(33, 127))
        token = u''.join([ru() for _ in xrange(16)])
        try:
            self.session.token = token
            self.session.timestamp = datetime.now()
            self.session.save()
            session = self.session
        except ObjectDoesNotExist:
            session = Session(token=token, timestamp=datetime.now(), user=self)
            session.save()
        return session


class StoredPublicKey(models.Model):
    """
    This class is used to store public keys. The matching RSA object can be
    created with the get_key method.
    """
    N = models.CharField(max_length=1000)
    e = models.BigIntegerField()
    key_hash = models.CharField(max_length=64)
    user = models.ForeignKey(User, related_name='keys')

    @classmethod
    def create(cls, user, n, e):
        """
        Creates a storedPublicKey and calculates the hash for the key.

        @param user: User instance
        @param n: string
        @param e: long
        @return: StoredPublicKey
        """
        hasher = sha256()
        hasher.update(n + str(e))
        stored_key = cls(user=user, N=n, e=e, key_hash=hasher.hexdigest())
        stored_key.save()
        return stored_key

    def get_key(self):
        """
        Generates the RSA object from the stored data. Use this object for
        encryption and verification.

        @return: RSA key object
        """
        return RSA.construct((long(self.N), long(self.e)))


class Session(models.Model):
    """
    The session saves the session token used for verification.
    """
    token = models.CharField(max_length=16, primary_key=True)
    timestamp = models.DateTimeField()
    user = models.OneToOneField(User, related_name='session')

    def get_encrypted_token(self, key):
        """
        This method returns the session token encrypted with the key.

        @param key: RSA public key object
        @return:
        """
        cipher = PKCS1_OAEP.new(key)
        return b16encode(cipher.encrypt(self.token))