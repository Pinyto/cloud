# coding=utf-8
"""
This File is part of Pinyto
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