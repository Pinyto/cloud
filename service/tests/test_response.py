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
