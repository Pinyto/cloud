# coding=utf-8
"""
In this file is the model definition for Pinyto users and for sessions.

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

from django.db import models
from django.dispatch import receiver
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from base64 import b64encode
from hashlib import sha256
from django.utils import timezone
from pinytoCloud.helpers import create_token


class User(models.Model):
    """
    This is an user object. Users have a username and a list of public keys
    for authentication.
    """
    name = models.CharField(max_length=30, primary_key=True)  #: (str) The username used for identifying the account
    time_budget = models.FloatField()  #: (float) The time budget of the user
    storage_budget = models.FloatField()  #: (float) The storage budget of the user
    current_storage = models.BigIntegerField()  #: (int) Current storage usage in bytes
    last_calculation_time = models.DateTimeField()  #: (int) Timestamp of the last time the budget was calculated

    def __str__(self):
        return self.name

    def start_session(self, key_db_object):
        """
        Creates a session object with a new random token.
        If there is an existing session it will be overwritten

        :param key_db_object:
        :type key_db_object: StoredPublicKey
        :rtype: Session
        """
        try:
            session = self.sessions.filter(key=key_db_object).all()[0]
            session.token = create_token()
            session.timestamp = timezone.now()
            session.save()
        except IndexError:
            session = Session(
                token=create_token(),
                timestamp=timezone.now(),
                key=key_db_object,
                user=self)
            session.save()
        return session

    def calculate_time_and_storage(self, added_time, new_storage):
        """
        This method updates the time- and storage budget of the user. The changed budget
        and the corresponding variables are saved.

        :param added_time: added time in milliseconds
        :type added_time: int
        :param new_storage: new storage in bytes
        :type new_storage: int
        """
        now = timezone.now()
        self.time_budget = self.time_budget + added_time
        self.storage_budget += self.current_storage * (now - self.last_calculation_time).total_seconds()
        self.last_calculation_time = now
        self.current_storage = new_storage
        self.save()


@receiver(models.signals.post_init, sender=User)
def initialize_budgets(sender, instance, **kwargs):
    """
    Initialization for users. All users are initialized with empty budgets.

    :param sender: User class
    :param instance: User
    :param kwargs: other params of __init__()
    """
    if not instance.time_budget:
        instance.time_budget = 0.0
    if not instance.storage_budget:
        instance.storage_budget = 0.0
    if not instance.current_storage:
        instance.current_storage = 0
    if not instance.last_calculation_time:
        instance.last_calculation_time = timezone.now()


class StoredPublicKey(models.Model):
    """
    This class is used to store public keys. The matching RSA object can be
    created with the get_key method.
    """
    #: (str) The first 10 characters of a sha256 hash computed from ``n + e``.
    key_hash = models.CharField(max_length=10, primary_key=True, unique=True)
    #: (str) N is a very big prime number so we have to save it as a string.
    N = models.CharField(max_length=1000)
    #: (long) e is not a very big number so we store it as a big integer.
    e = models.BigIntegerField()
    #: (User) This is the foreign-key to the User who owns this key.
    user = models.ForeignKey(User, related_name='keys')
    #: (boolean) Keys can be deactivated. By default keys are active.
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.key_hash + ':: N: ' + self.N + ' e: ' + str(self.e) + ' ' + str(self.user)

    @classmethod
    def create(cls, user, n, e):
        """
        Creates a storedPublicKey and calculates the hash for the key.

        :param user:
        :type user: pinytoCloud.models.User
        :param n:
        :type n: str
        :param e:
        :type e: int
        :rtype: StoredPublicKey
        """
        hasher = sha256()
        hasher.update((n + str(e)).encode('utf-8'))
        stored_key = cls(user=user, N=n, e=e, key_hash=hasher.hexdigest()[:10])
        stored_key.save()
        return stored_key

    def get_key(self):
        """
        Generates the RSA object from the stored data. Use this object for
        encryption and verification.

        :rtype: cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey
        """
        return rsa.RSAPublicNumbers(self.e, int(self.N)).public_key(default_backend())


class Session(models.Model):
    """
    The session saves the session token used for verification.
    """
    #: (string) The token consists of 16 random characters.
    token = models.CharField(max_length=16)
    #: (int) The timestamp is reset with every request. It can be used to delete old sessions with a cron job.
    timestamp = models.DateTimeField()
    #: (pinytoCloud.models.User) The reference to the user who own this session.
    user = models.ForeignKey(User, related_name='sessions')
    #: (pinytoCloud.models.StoredPublicKey) The reference to the key used to start the session.
    key = models.OneToOneField(StoredPublicKey, related_name='related_session', unique=True)

    def __str__(self):
        return self.token + ' (' + str(self.timestamp) + ') ' + str(self.user) + ' Key: ' + self.key.key_hash

    def get_encrypted_token(self):
        """
        This method returns the session token encrypted with the key.

        :returns: base64 encoded encrypted token
        :rtype: str
        """
        encrypted_token = self.key.get_key().encrypt(
            self.token.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )
        return str(b64encode(encrypted_token), encoding='utf-8')


class Assembly(models.Model):
    """
    An Assembly is a collection of ApiFunctions and Jobs which can be installed and activated
    for the user en block. Each assembly has a unique identifier referencing the exact set of
    ApiFunctions and Jobs. The original author can update his assembly and all users who
    installed it automatically load the new version. A user may fork an assembly which creates
    an exact clone with the forking user as new author.
    """
    #: (string) The name of the assembly is capped to 42 characters.
    name = models.CharField(max_length=42)
    #: (pinytoCloud.models.User) Foreign-key to the user who owns the assembly.
    author = models.ForeignKey(User, related_name='assemblies')
    #: (string) A description what the assembly does. This is displayed when the assembly gets installed.
    description = models.TextField()
    #: A list of users who installed this assembly.
    installed_at = models.ManyToManyField(User, related_name='installed_assemblies')
    #: (boolean) If this flag is true the assembly can only access documents with the assembly attribute
    #: matching the name of this assembly. If set to true the user may be able not to check the sourcecode
    #: of this assembly because he can be sure that it does not read, change or delete other data than its
    #: own.
    only_own_data = models.BooleanField(default=True)

    class Meta:
        unique_together = (("author", "name"),)

    def __str__(self):
        return self.author.name + '/' + self.name

    def fork(self, new_user):
        """
        A user may fork an assembly which creates an exact clone with the forking user as new
        author.

        :param new_user:
        :type new_user: pinytoCloud.models.User
        :rtype: pinytoCloud.models.Assembly
        """
        fork = Assembly()
        fork.name = self.name
        fork.author = new_user
        fork.description = self.description
        fork.save()
        return fork


class ApiFunction(models.Model):
    """
    ApiFunctions answer to requests to a url in the format user/assemblyname/functionname.
    They always return a json response.
    """
    #: (string) The name of the function is the last part of the path that has to be called to execute this code.
    name = models.CharField(max_length=42, primary_key=True)
    #: (string) The python code of the function. The signature of the call has a very special format. Please see
    #: `Assemblies <assemblies.html>`_ for more information.
    code = models.TextField()
    #: (pinytoCloud.models.Assembly) Reference to the Assembly the function belongs to.
    assembly = models.ForeignKey(Assembly, related_name='api_functions')

    def __str__(self):
        return self.name + ' from Assembly: ' + self.assembly.author.name + '/' + self.assembly.name


class Job(models.Model):
    """
    Jobs are scripts that can be run on a regular basis or which are queued for later
    execution (if the ApiFunction tries to return something early but additional work
    needs to be done). This model saves these scripts. Jobs do not return anything but
    save their work to the database. Results can be polled by ApiFunctions.
    """
    #: (string) The name of the job. This name can be used to execute the job. To invoke this in a API-call
    #: simply save a document with type:'job' and this name.
    name = models.CharField(max_length=42, primary_key=True)
    #: (string) The python code of the function. The signature of the call has a very special format. Please see
    #: `Assemblies <assemblies.html>`_ for more information.
    code = models.TextField()
    #: (pinytoCloud.models.Assembly) Reference to the Assembly the job belongs to.
    assembly = models.ForeignKey(Assembly, related_name='jobs')
    #: (int) Execute every schedule minutes (0 means never).
    schedule = models.IntegerField(default=0)

    def __str__(self):
        return self.name + ' from Assembly: ' + self.assembly.author.name + '/' + self.assembly.name + \
            ' Scheduled: ' + str(self.schedule)