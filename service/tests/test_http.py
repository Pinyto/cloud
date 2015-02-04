# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from service.http import Http


class TestHttps(TestCase):
    def test_wrong_url(self):
        self.assertEqual(Http.get('http://nix.uns1nnsdomain.gibtsnicht/pfad/nach/nirgendwo'), "")
        self.assertEqual(Http.post('http://nix.uns1nnsdomain.gibtsnicht/pfad/nach/nirgendwo'), "")

    def test_get_connect_to_google(self):
        response = Http.get('https://www.google.de/')
        self.assertEqual(type(response), str)
        self.assertGreater(len(response), 0)

    def test_get_connect_to_pinyto(self):
        response = Http.get('https://pinyto.de/')
        self.assertEqual(type(response), str)
        self.assertGreater(len(response), 0)

    def test_post_connect_to_google(self):
        response = Http.post(
            'https://accounts.google.com/ServiceLoginAuth',
            {'@Email': "a@bc.de", '@Passwd': "******"})
        self.assertEqual(type(response), str)
        self.assertGreater(len(response), 0)