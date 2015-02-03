# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from service.http import Https


class TestHttps(TestCase):
    def test_wrong_url(self):
        self.assertEqual(Https.get('nix.uns1nnsdomain.gibtsnicht', '/pfad/nach/nirgendwo'), "")
        self.assertEqual(Https.post('nix.uns1nnsdomain.gibtsnicht', '/pfad/nach/nirgendwo'), "")

    def test_get_connect_to_google(self):
        response = Https.get('www.google.de', '/')
        self.assertEqual(type(response), str)
        self.assertGreater(len(response), 0)

    def test_get_connect_to_pinyto(self):
        response = Https.get('pinyto.de', '/')
        self.assertEqual(type(response), str)
        self.assertGreater(len(response), 0)

    def test_post_connect_to_google(self):
        response = Https.post('accounts.google.com', '/ServiceLoginAuth', {'@Email': "a@bc.de", '@Passwd': "******"})
        self.assertEqual(type(response), str)
        self.assertGreater(len(response), 0)