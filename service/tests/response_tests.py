from __future__ import division, print_function, unicode_literals

from django.test import TestCase
from django.http.response import HttpResponse
from service.response import json_response
from database.helpers import create_user


class TestResponse(TestCase):
    def setUp(self):
        #self.hans = create_user('hans')
        pass

    def test_json_response(self):
        data = {'a': 12, 'b': ['c', 4, {1: 5, 2: 'd'}], 9: 14.5}
        response = json_response(data)
        self.assertEqual(type(response), HttpResponse)
        self.assertEqual(200, response.status_code)
        self.assertEqual('{"a": 12, "9": 14.5, "b": ["c", 4, {"1": 5, "2": "d"}]}', response.content)
