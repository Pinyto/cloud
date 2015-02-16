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
from unittest.mock import patch
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