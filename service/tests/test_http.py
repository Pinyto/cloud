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
        self.assertGreater(len(Https.get('www.google.de', '/')), 0)

    def test_post_connect_to_google(self):
        self.assertGreater(len(
            Https.post('accounts.google.com', '/ServiceLoginAuth', {'@Email': "a@bc.de", '@Passwd': "******"})
        ), 0)