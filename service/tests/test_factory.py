# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from service.models import Factory
from service.http import Http
from service.parsehtml import ParseHtml
from api_prototype.models import CanNotCreateNewInstanceInTheSandbox


class TestFactory(TestCase):
    def test_create_Http(self):
        factory = Factory()
        https = factory.create('Http')
        self.assertEqual(type(https), Http)

    def test_create_ParseHtml(self):
        factory = Factory()
        parse_html = factory.create('ParseHtml', '<body><p>Yes</p></body>')
        self.assertEqual(type(parse_html), ParseHtml)

    def create_Nonsense(self):
        factory = Factory()
        factory.create('Nonsense')

    def test_unknown_class(self):
        self.assertRaises(CanNotCreateNewInstanceInTheSandbox, self.create_Nonsense)