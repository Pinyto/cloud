# coding=utf-8
"""
This File is part of Pinyto
"""
from django.test import TestCase
from django.core.urlresolvers import reverse
import json

from pinytoCloud.models import User


class AuthenticateTest(TestCase):
    def setUp(self):
        self.hugo = User(name='hugo')

    def test_unknown_user_returns_error(self):
        response = self.client.post(reverse('authenticate'), {'username': 'Max', 'keyhash': 'wrong'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "User 'Max' is unknown. Please register first.")