# coding=utf-8
"""
This File is part of Pinyto
"""
from django.test import TestCase
from pinytoCloud.helpers import create_token


class HelpersTest(TestCase):
    def test_create_token(self):
        for i in range(100):
            token = create_token(i)
            self.assertEqual(i, len(token))
            for char in token:
                self.assertIn(char, ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'])