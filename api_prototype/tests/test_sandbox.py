# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from pinytoCloud.models import User
from api_prototype.sandbox import safely_exec


class TestSandbox(TestCase):
    def test_safely_exec(self):
        code = "print('Hallo')\nprint('Welt !')"
        hugo = User(name='hugo')
        hugo.save()
        result, time = safely_exec(code, hugo)
        self.assertEqual(result, "Hallo\nWelt !\n")
        self.assertTrue(time < 1)