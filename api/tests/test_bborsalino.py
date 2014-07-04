# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from django.test.client import Client
from pinytoCloud.models import User
import json


class TestBBorsalino(TestCase):
    def setUp(self):
        self.bborsalino = User(name='bborsalino')
        self.bborsalino.save()

    def test_index(self):
        test_client = Client()
        response = test_client.post('/bborsalino/Librarian/index', {'ean': '1234567890123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['index'], [])