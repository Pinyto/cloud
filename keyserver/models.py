# coding=utf-8
"""
Pinyto cloud - A secure cloud database for your personal data
Copyright (C) 2019 Pina Merkert <pina@pinae.net>

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

from django.db import models
from hashlib import sha256
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from keyserver.helper import create_salt


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
    hash_iterations = models.IntegerField(default=10000)
    hash = models.CharField(max_length=32)
    N = models.CharField(max_length=1000)
    e = models.BigIntegerField()
    d = models.CharField(max_length=1000)
    p = models.CharField(max_length=1000)
    q = models.CharField(max_length=1000)

    @staticmethod
    def hash_password(password, salt, hash_iterations):
        hash_string = password + salt
        for i in range(hash_iterations):
            hasher = sha256()
            hasher.update(hash_string.encode('utf-8'))
            hash_string = hasher.hexdigest()
        return hash_string[:32]

    @classmethod
    def create(cls, name, password='', hash_iterations=420):
        """
        Creates an account with hashed password, new random salt and 4096 bit RSA key pair.

        :param name:
        :type name: str
        :param password: (technically this is an optional parameter but in reality you should not
                          use empty passwords)
        :type password: str
        :param hash_iterations: (optional)
        :type hash_iterations: int
        :return: An Account instance already saved to the database
        :rtype: keyserver.models.Account
        """
        salt = create_salt(10)
        hash_string = cls.hash_password(password, salt, hash_iterations)
        key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
        account = cls(name=name,
                      salt=salt,
                      hash_iterations=hash_iterations,
                      hash=hash_string,
                      N=key.public_key().public_numbers().n,
                      e=key.public_key().public_numbers().e,
                      d=key.private_numbers().d,
                      p=key.private_numbers().p,
                      q=key.private_numbers().q)
        account.save()
        return account

    def check_password(self, password):
        """
        This method checks if the given password is valid by comparing it to the stored hash.

        :param password:
        :type password: str
        :rtype: boolean
        """
        hash_string = self.hash_password(password, self.salt, self.hash_iterations)
        return hash_string == self.hash

    def change_password(self, password, hash_iterations=420):
        """
        Changes the password to the supplied one.
        hash_iterations are optional but can be used to upgrade the passwords to faster servers.

        :param password:
        :type password: str
        :param hash_iterations: (optional)
        :type hash_iterations: int
        """
        self.salt = create_salt(10)
        hash_string = self.hash_password(password, self.salt, hash_iterations)
        self.hash_iterations = hash_iterations
        self.hash = str(hash_string, encoding='utf-8')
        self.save()
