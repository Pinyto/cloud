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