# coding=utf-8
"""
In this file is the model definition for Pinyto users and for sessions.
"""

from django.db import models
from Crypto.PublicKey import RSA
from hashlib import sha256


class User(models.Model):
    """
    This is an user object. Users have a username and a list of public keys
    for authentication.
    """
    name = models.CharField(max_length=30, primary_key=True)


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
        return RSA.construct((self.N, self.e))


class Session(models.Model):
    """
    The session saves the session token used for verification.
    """
    token = models.CharField(max_length=10, primary_key=True)
    user = models.OneToOneField(User, related_name='session')