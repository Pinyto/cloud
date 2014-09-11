# coding=utf-8
"""
This File is part of Pinyto
"""

from django.db import models
from hashlib import sha256
from Crypto import Random
from Crypto.PublicKey import RSA
from helper import create_salt


class Account(models.Model):
    """
    A Pinyto account consists of a username, a password and
    a pair of asymmetric keys. The keys are used for the
    authentication with a pinyto server which stores the
    data. Username and password are the credentials memorized
    by the user which he can use to access his keys.

    The password is not stored but a hash. If a password is
    supplied the salt is added and the concatenation is hashed.
    The hash of the hash gets hashed until the password was
    hashed for hash_iteration times. The algorithm which is used
    is SHA256. After the last iteration the hash can be compared
    to the stored hash. If they match the password is correct.
    """
    name = models.CharField(max_length=30, primary_key=True)
    salt = models.CharField(max_length=10)
    hash_iterations = models.IntegerField(default=42000)
    hash = models.CharField(max_length=32)
    N = models.CharField(max_length=1000)
    e = models.BigIntegerField()
    d = models.CharField(max_length=1000)

    @classmethod
    def create(cls, name, password=u'', hash_iterations=420):
        """
        Creates an account with hashed password, new random salt and 3072 bit RSA key pair.

        @param name: string
        @param password: string
        @param hash_iterations: int
        @return: Account (already saved to the database)
        """
        salt = create_salt(10)
        hash_string = password + salt
        for i in range(hash_iterations):
            hasher = sha256()
            hasher.update(hash_string)
            hash_string = hasher.hexdigest()
        key = RSA.generate(3072, Random.new().read)
        account = cls(name=name,
                      salt=salt,
                      hash_iterations=hash_iterations,
                      hash=unicode(hash_string),
                      N=unicode(key.n),
                      e=key.e,
                      d=unicode(key.d))
        account.save()
        return account

    def check_password(self, password):
        """
        This method checks if the given password is valid by comparing it to the stored hash.

        @param password: string
        @return: boolean
        """
        hash_string = unicode(password) + self.salt
        for i in range(self.hash_iterations):
            hasher = sha256()
            hasher.update(hash_string)
            hash_string = hasher.hexdigest()
        return unicode(hash_string) == self.hash

    def change_password(self, password, hash_iterations=420):
        """
        Changes the password to the supplied one.
        hash_iterations are optional but can be used to upgrade the passwords to faster servers.

        @param password: string
        @param hash_iterations: int
        @return: nothing
        """
        self.salt = create_salt(10)
        hash_string = password + self.salt
        for i in range(hash_iterations):
            hasher = sha256()
            hasher.update(hash_string)
            hash_string = hasher.hexdigest()
        self.hash_iterations = hash_iterations
        self.hash = unicode(hash_string)
        self.save()