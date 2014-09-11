# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from django.test.client import RequestFactory
from pymongo import MongoClient
from pymongo.collection import Collection
from service.database import CollectionWrapper
from api_prototype.sandbox import safely_exec


class TestSandbox(TestCase):
    def setUp(self):
        self.collection = Collection(MongoClient().pinyto, 'hugo_test')
        self.collection_wrapper = CollectionWrapper(self.collection)
        self.factory = RequestFactory()

    def tearDown(self):
        self.collection.drop()

    def test_safely_exec(self):
        code = "print('Hallo')\nprint('Welt !')\nreturn ''"
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertEqual(result, "Hallo\nWelt !\n\n")
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
            u'result so far': u'',
            u'error': {
                u'exception': u"<type 'exceptions.ZeroDivisionError'>",
                u'message': u'integer division or modulo by zero'
            }})
        self.assertTrue(time < 1)

    def test_return_statement(self):
        code = """return 'abc'"""
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertEqual(result, u'abc\n')
        self.assertTrue(time < 1)

    def test_safely_exec_variable_assignment(self):
        code = "string = 'Hallo Welt.'\nreturn string"
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertEqual(result, "Hallo Welt.\n")
        self.assertTrue(time < 1)

    def test_safely_exec_db_access(self):
        self.collection_wrapper.insert({'test': 1, 'a': "Hallo"})
        self.collection_wrapper.insert({'test': 1, 'b': long(34578629385748347)})
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
            "[1, 1]\n")
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
        self.assertEqual(result, "1\n")
        self.assertTrue(time < 1)

    def test_safely_exec_parsehtml_find_element_and_get_attribute_value(self):
        code = """html = '<html><body><div style="width: 100px;">DIV</div>'
html += '<table><tr><td>A</td><td>3</td></tr></table></body></html>'
soup = factory.create('ParseHtml', html)
return soup.find_element_and_get_attribute_value([{'tag': 'div'}], 'style')"""
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertEqual(result, "width: 100px;\n")
        self.assertTrue(time < 1)

    def test_safely_exec_parsehtml_find_element_and_collect_table_like_information(self):
        code = """html = '<html><body><div style="width: 100px;">DIV</div>'
html += '<table><tr><td>A</td><td>3</td></tr></table></body></html>'
soup = factory.create('ParseHtml', html)
return soup.find_element_and_collect_table_like_information(
    [{'tag': 'table'}, {'tag': 'tr'}],
    {'a': {'search tag': 'td', 'captions': ['A'], 'content tag': 'td'}})"""
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertEqual(result, "{u'a': u'3'}\n")
        self.assertTrue(time < 1)

    def test_connect_to_twitter(self):
        code = """https = factory.create('Https')
return len(str(https.get('twitter.com', '/')))"""
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertGreater(int(result), 0)
        self.assertTrue(time < 1)

    def test_request_get_param(self):
        code = """return request.POST.get('a')"""
        result, time = safely_exec(code, self.factory.post('/', {'a': '123'}), self.collection_wrapper)
        self.assertEqual(result, "123\n")
        self.assertTrue(time < 1)

    def test_json_dumps(self):
        code = """return json.dumps({'a': 42})"""
        result, time = safely_exec(code, self.factory.post('/'), self.collection_wrapper)
        self.assertEqual(result, u'{"a": 42}\n')
        self.assertTrue(time < 1)