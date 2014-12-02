# coding=utf-8
"""
In this file is the model definition for Pinyto users and for sessions.
"""

from django.db import models
from django.dispatch import receiver
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
    time_budget = models.FloatField()
    storage_budget = models.FloatField()
    current_storage = models.BigIntegerField()
    last_calculation_time = models.DateTimeField()

    def __str__(self):
        return self.name

    def start_session(self, key_db_object):
        """
        Creates a session object with a new random token.
        If there is an existing session it will be overwritten

        @param key_db_object: StoredPublicKey
        @return: Session object
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

    def calculate_time_and_storage(self, added_time, new_storage):
        """
        This method updates the time- and storage budget of the user. The changed budget
        and the corresponding variables are saved.

        @param added_time: time
        @param new_storage: int
        """
        now = datetime.now(tzlocal())
        self.time_budget = self.time_budget + added_time
        self.storage_budget += self.current_storage * (now - self.last_calculation_time).total_seconds()
        self.last_calculation_time = now
        self.current_storage = new_storage
        self.save()


@receiver(models.signals.post_init, sender=User)
def initialize_budgets(sender, instance, **kwargs):
    """
    Initialization for users. All users are initialized with empty budgets.

    @param sender: User class
    @param instance: User
    @param kwargs: other params of __init__()
    """
    if not instance.time_budget:
        instance.time_budget = 0.0
    if not instance.storage_budget:
        instance.storage_budget = 0.0
    if not instance.current_storage:
        instance.current_storage = 0
    if not instance.last_calculation_time:
        instance.last_calculation_time = datetime.now(tzlocal())


class StoredPublicKey(models.Model):
    """
    This class is used to store public keys. The matching RSA object can be
    created with the get_key method.
    """
    key_hash = models.CharField(max_length=10, primary_key=True, unique=True)
    N = models.CharField(max_length=1000)
    e = models.BigIntegerField()
    user = models.ForeignKey(User, related_name='keys')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.key_hash + ':: N: ' + self.N + ' e: ' + str(self.e) + ' ' + str(self.user)

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
    token = models.CharField(max_length=16)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(User, related_name='sessions')
    key = models.OneToOneField(StoredPublicKey, related_name='related_session', unique=True)

    def __str__(self):
        return self.token + ' (' + str(self.timestamp) + ') ' + str(self.user) + ' Key: ' + self.key.key_hash

    def get_encrypted_token(self):
        """
        This method returns the session token encrypted with the key.

        @return: base16 encoded encrypted token which is a string
        """
        cipher = PKCS1_OAEP.new(self.key.get_key())
        return b16encode(cipher.encrypt(self.token.encode('ascii')))


class Assembly(models.Model):
    """
    An Assembly is a collection of ApiFunctions and Jobs which can be installed and activated
    for the user en block. Each assembly has a unique identifier referencing the exact set of
    ApiFunctions and Jobs. The original author can update his assembly and all users who
    installed it automatically load the new version. A user may fork an assembly which creates
    an exact clone with the forking user as new author.
    """
    name = models.CharField(max_length=42)
    author = models.ForeignKey(User, related_name='assemblies')
    description = models.TextField()
    installed_at = models.ManyToManyField(User, related_name='installed_assemblies')

    class Meta:
        unique_together = (("author", "name"),)

    def __str__(self):
        return self.author.name + '/' + self.name

    def fork(self, new_user):
        """
        A user may fork an assembly which creates an exact clone with the forking user as new
        author.

        @param new_user: User
        @return: Assembly
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
    name = models.CharField(max_length=42, primary_key=True)
    code = models.TextField()
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
    name = models.CharField(max_length=42, primary_key=True)
    code = models.TextField()
    assembly = models.ForeignKey(Assembly, related_name='jobs')
    schedule = models.IntegerField(default=0)  # each schedule minutes (0 means never)

    def __str__(self):
        return self.name + ' from Assembly: ' + self.assembly.author.name + '/' + self.assembly.name + \
               ' Scheduled: ' + str(self.schedule)