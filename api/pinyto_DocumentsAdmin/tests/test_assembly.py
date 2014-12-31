# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from mock import patch
from django.test.client import Client
from pymongo import MongoClient
from pymongo.collection import Collection
from service.database import CollectionWrapper
from pinytoCloud.models import User, StoredPublicKey, Assembly, ApiFunction, Job
import json
import time


class TestDocumentsAdmin(TestCase):
    def setUp(self):
        self.pinyto = User(name='pinyto')
        self.pinyto.save()
        self.collection = Collection(MongoClient().pinyto, 'Hugo')
        self.collection.remove({})
        self.collection_wrapper = CollectionWrapper(self.collection, 'pinyto/DocumentsAdmin')

    def mock_check_token(self):
        """
        Mocks the token check.
        @return: Session
        """
        hugo = User(name='Hugo')
        hugo.save()
        key = StoredPublicKey.create(hugo, '13', 5)
        return hugo.start_session(key)

    @patch('pinytoCloud.checktoken.check_token', mock_check_token)
    def test_index(self):
        pass