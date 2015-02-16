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
from database.helpers import get_str_or_discard, get_tags
import datetime


class TestGetStrOrDiscard(TestCase):
    def test_str(self):
        self.assertEqual(get_str_or_discard('abc'), 'abc')

    def test_int(self):
        self.assertEqual(get_str_or_discard(42), '42')

    def test_float(self):
        self.assertEqual(get_str_or_discard(1.37), '1.37')

    def test_list(self):
        self.assertEqual(get_str_or_discard([1, 4, 7]), '')

    def test_dict(self):
        self.assertEqual(get_str_or_discard({'a': 7}), '')

    def test_datetime(self):
        self.assertEqual(get_str_or_discard(datetime.datetime.now()), '')

    def test_unicode(self):
        self.assertEqual(get_str_or_discard(u"abc"), 'abc')


class TestGetTags(TestCase):
    def test_string(self):
        self.assertListEqual(get_tags('abc'), ['abc'])

    def test_list_of_strings(self):
        self.assertListEqual(get_tags(['a', 'b', 'c']), ['a', 'b', 'c'])

    def test_dict(self):
        self.assertListEqual(get_tags({'a': 42}), [])

    def test_list_of_strings_and_numbers(self):
        self.assertListEqual(get_tags([1, 'a', 3.3]), ['1', 'a', '3.3'])

    def test_list_with_invalid_types(self):
        self.assertEqual(get_tags(['a', datetime.datetime.now(), {'b': 44}, 2, [1, 5, 'oho'], 2.1]), ['a', '2', '2.1'])