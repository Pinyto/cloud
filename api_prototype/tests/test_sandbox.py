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
from django.test.client import RequestFactory
from database.mongo_connection import MongoConnection
from pymongo.collection import Collection
from service.database import CollectionWrapper
from api_prototype.sandbox import safely_exec
import json


class TestSandbox(TestCase):
    def setUp(self):
        self.db = MongoConnection.create_mongo_client()['test_pinyto']
        self.collection = Collection(self.db, 'hugo_test')
        self.collection_wrapper = CollectionWrapper(self.collection, 'some/assembly')
        self.factory = RequestFactory()

    def tearDown(self):
        self.collection.drop()

    def test_safely_exec(self):
        code = "print('Hallo')\nprint('Welt !')\nreturn ''"
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertEqual(result, {'result': u'Hallo\nWelt !\n\n'})
        self.assertTrue(time < 1)

    def test_safely_exec_harmful_code(self):
        code = "print('Contents of /etc/:')\nimport os\nlist = os.listdir('/etc/')\nprint(list)"
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertEqual(
            result,
            {u'error': u'The code could not be executed because it tried to do something illegal.'})
        self.assertTrue(time < 1)

    def test_safely_exec_throw_exception(self):
        code = "a = 1 / 0"
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertEqual(result, {
            'result so far': '',
            'error': {
                'exception': "<class 'ZeroDivisionError'>",
                'message': 'division by zero'
            }})
        self.assertTrue(time < 1)

    def test_return_statement(self):
        code = """return 'abc'"""
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertEqual(result, {'result': u'abc\n'})
        self.assertTrue(time < 1)

    def test_safely_exec_variable_assignment(self):
        code = "string = 'Hallo Welt.'\nreturn string"
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertEqual(result, {'result': u"Hallo Welt.\n"})
        self.assertTrue(time < 1)

    def test_safely_exec_db_access(self):
        self.collection_wrapper.insert({'test': 1, 'a': "Hallo"})
        self.collection_wrapper.insert({'test': 1, 'b': 34578629385748347})
        self.collection_wrapper.insert({'test': 2, 'a': "Bar"})
        code = """response = '['
for document in db.find({'test': 1}):
    response += str(document['test']) + ', '
response = response[:-2] + ']'
return response
"""
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertEqual(
            result,
            {'result': u"[1, 1]\n"})
        self.assertTrue(time < 1)

    def test_safely_exec_parsehtml_contains(self):
        code = """html = '<html><body><div style="width: 100px;">DIV</div>'
html += '<table><tr><td>A</td><td>3</td></tr></table></body></html>'
soup = factory.create('ParseHtml', html)
if soup.contains([{'tag': 'div'}]):
    return 1
else:
    return 0"""
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertEqual(result, {'result': u"1\n"})
        self.assertTrue(time < 1)

    def test_safely_exec_parsehtml_find_element_and_get_attribute_value(self):
        code = """html = '<html><body><div style="width: 100px;">DIV</div>'
html += '<table><tr><td>A</td><td>3</td></tr></table></body></html>'
soup = factory.create('ParseHtml', html)
return soup.find_element_and_get_attribute_value([{'tag': 'div'}], 'style')"""
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertEqual(result, {'result': u"width: 100px;\n"})
        self.assertTrue(time < 1)

    def test_safely_exec_parsehtml_find_element_and_collect_table_like_information(self):
        code = """html = '<html><body><div style="width: 100px;">DIV</div>'
html += '<table><tr><td>A</td><td>3</td></tr></table></body></html>'
soup = factory.create('ParseHtml', html)
return soup.find_element_and_collect_table_like_information(
    [{'tag': 'table'}, {'tag': 'tr'}],
    {'a': {'search tag': 'td', 'captions': ['A'], 'content tag': 'td'}})"""
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertEqual(result, {'result': "{'a': '3'}\n"})
        self.assertTrue(time < 1)

    def test_connect_to_pinyto(self):
        code = """http = factory.create('Http')
return len(str(http.get('https://pinyto.de/')))"""
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertIn('result', result)
        self.assertGreater(int(result['result']), 0)
        self.assertTrue(time < 1)

    def test_request_body(self):
        code = """return str(request.body, encoding='utf-8')"""
        result, time = safely_exec(code, self.factory.post(
            '/',
            json.dumps({'a': '123'}),
            content_type='application/json'
        ), self.collection_wrapper)
        self.assertIn('result', result)
        self.assertEqual(json.loads(result['result']), {"a": "123"})
        self.assertTrue(time < 1)

    def test_request_get_param(self):
        code = """return request.POST.get('a')"""
        result, time = safely_exec(code, self.factory.post(
            '/',
            {'a': '123'}
        ), self.collection_wrapper)
        self.assertEqual(result, {'result': u"123\n"})
        self.assertTrue(time < 1)

    def test_json_dumps(self):
        code = """return json.dumps({'a': 42})"""
        result, time = safely_exec(
            code,
            self.factory.post('/', content_type='application/json'),
            self.collection_wrapper)
        self.assertEqual(result, {'result': u'{"a": 42}\n'})
        self.assertTrue(time < 1)