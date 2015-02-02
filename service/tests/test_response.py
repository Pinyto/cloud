# coding=utf-8
from __future__ import division, print_function, unicode_literals

from django.test import TestCase
from django.http.response import HttpResponse
from service.response import json_response
import json


class TestResponse(TestCase):
    def setUp(self):
        pass

    def test_json_response(self):
        data = {'a': 12, 'b': ['c', 4, {'1': 5, '2': 'd'}], '9': 14.5}
        response = json_response(data)
        self.assertEqual(type(response), HttpResponse)
        self.assertEqual(200, response.status_code)
        res = json.loads(str(response.content, encoding='utf-8'))
        self.assertIn('a', res)
        self.assertEqual(res['a'], 12)
        self.assertIn('b', res)
        self.assertEqual(res['b'][0], 'c')
        self.assertEqual(res['b'][1], 4)
        self.assertIn('1', res['b'][2])
        self.assertEqual(res['b'][2]['1'], 5)
        self.assertIn('2', res['b'][2])
        self.assertEqual(res['b'][2]['2'], 'd')
        self.assertIn('9', res)
        self.assertAlmostEqual(res['9'], 14.5, places=10)
