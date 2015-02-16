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