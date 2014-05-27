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
from dateutil.tz import tzlocal
from pinytoCloud.helpers import create_token


class User(models.Model):
    """
    This is an user object. Users have a username and a list of public keys
    for authentication.
    """
    name = models.CharField(max_length=30, primary_key=True)

    def start_session(self, key_db_object):
        """
        Creates a session object with a new random token.
        If there is an existing session it will be overwritten

        @param key_db_object: StoredPublicKey
        @return: User object
        """
        try:
            session = self.sessions.filter(key=key_db_object).all()[0]
            session.token = create_token()
            session.timestamp = datetime.now(tzlocal())
            session.save()
        except IndexError:
            session = Session(
                token=create_token(),
                timestamp=datetime.now(tzlocal()),
                key=key_db_object,
                user=self)
            session.save()
        return session


class StoredPublicKey(models.Model):
    """
    This class is used to store public keys. The matching RSA object can be
    created with the get_key method.
    """
    key_hash = models.CharField(max_length=10, primary_key=True)
    N = models.CharField(max_length=1000)
    e = models.BigIntegerField()
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
        stored_key = cls(user=user, N=n, e=e, key_hash=hasher.hexdigest()[:10])
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
    user = models.ForeignKey(User, related_name='sessions')
    key = models.OneToOneField(StoredPublicKey, related_name='related_session')

    def get_encrypted_token(self):
        """
        This method returns the session token encrypted with the key.

        @param key: RSA public key object
        @return:
        """
        cipher = PKCS1_OAEP.new(self.key.get_key())
        return b16encode(cipher.encrypt(self.token))