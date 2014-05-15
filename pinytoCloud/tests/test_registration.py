# coding=utf-8
"""
This File is part of Pinyto
"""
from django.test import TestCase
from django.core.urlresolvers import reverse
from pinytoCloud.models import User
import json


class RegisterTest(TestCase):
    def test_taken_username(self):
        self.hugo = User(name='hugo')
        self.hugo.save()
        response = self.client.post(reverse('register'), {'username': 'hugo', 'public_key': '{"N": "1", "e": "1"}'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Username 'hugo' is already taken. Try another username.")

    def test_no_username(self):
        response = self.client.post(reverse('register'), {'thing': '42'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "You have to supply a username.")

    def test_no_key_data(self):
        response = self.client.post(reverse('register'), {'username': 'hugo'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "You have to supply a public_key.")

    def test_key_data_in_a_wrong_format(self):
        response = self.client.post(reverse('register'), {'username': 'hugo', 'public_key': '{"No": "1", "ne": "1"}'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "The public_key is in the wrong format. The key data must consist of an N and an e."
        )

    def test_n_not_a_number(self):
        response = self.client.post(reverse('register'), {'username': 'hugo', 'public_key': '{"N": "abc", "e": "1"}'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Factor N in the public key is not a number. It has to be a long integer.")

    def test_e_not_a_number(self):
        response = self.client.post(
            reverse('register'),
            {'username': 'hugo', 'public_key': '{"N": ' + str(pow(2, 3072) - 7458345) + ', "e": "xxx"}'}
        )
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Factor e in the public key is not a number. It has to be a long integer.")

    def test_n_too_small(self):
        response = self.client.post(reverse('register'), {'username': 'hugo', 'public_key': '{"N": "3845", "e": "1"}'})
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Factor N in the public key is too small. Please use 3072 bit.")