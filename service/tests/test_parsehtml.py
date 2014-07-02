# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from service.parsehtml import ParseHtml


class TestParseHtml(TestCase):
    def test_contains(self):
        html = """
        <html>
        <head><title>Just a Test</title></head>
        <body>
            <h1>Heading</h1>
            <div data-custom="special">Te<i>x</i>t</div>
        </body>
        </html>"""
        soup = ParseHtml(html)
        self.assertTrue(soup.contains([{'tag': "div", 'attrs': {'data-custom': "special"}}]))
        self.assertTrue(soup.contains({'tag': "div", 'attrs': {'data-custom': "special"}}))
        self.assertTrue(soup.contains([{'tag': "div", 'attrs': {'data-custom': "special"}}, {'tag': "i"}]))
        self.assertFalse(soup.contains({'tag': "div", 'attrs': {'style': "something"}}))
        self.assertFalse(soup.contains({'tag': "span"}))

    def test_find_element_and_get_attribute_value(self):
        html = """
        <html>
        <head><title>Just a Test</title></head>
        <body>
            <h1>Heading</h1>
            <div data-custom="special" style="width: 20px;" class="inline">
                Text
                <span>Thing</span>
                <a href="location">Link</a>
                <a href="somewhere">another Link</a>
            </div>
        </body>
        </html>"""
        soup = ParseHtml(html)
        self.assertEqual(
            soup.find_element_and_get_attribute_value(
                [{'tag': "div", 'attrs': {'data-custom': "special"}}],
                'style'),
            'width: 20px;')
        self.assertEqual(
            soup.find_element_and_get_attribute_value(
                {'tag': "div", 'attrs': {'data-custom': "special"}},
                'style'),
            'width: 20px;')
        self.assertEqual(
            soup.find_element_and_get_attribute_value(
                [{'tag': "div", 'attrs': {'data-custom': "special"}}],
                'class'),
            ['inline'])
        self.assertEqual(
            soup.find_element_and_get_attribute_value(
                [{'tag': "div", 'attrs': {'data-custom': "special"}}],
                'id'),
            '')
        self.assertEqual(
            soup.find_element_and_get_attribute_value([{'tag': "span"}], 'id'),
            '')
        self.assertEqual(
            soup.find_element_and_get_attribute_value([
                    {'tag': "div", 'attrs': {'data-custom': "special"}},
                    {'tag': "a"}],
                'href'),
            'location')