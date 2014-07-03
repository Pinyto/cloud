# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from pymongo import MongoClient
from pymongo.collection import Collection
from service.database import CollectionWrapper
from api_prototype.sandbox import safely_exec


class TestSandbox(TestCase):
    def setUp(self):
        self.collection = Collection(MongoClient().pinyto, 'hugo_test')
        self.collection_wrapper = CollectionWrapper(self.collection)

    def tearDown(self):
        self.collection.drop()

    def test_safely_exec(self):
        code = "print('Hallo')\nprint('Welt !')"
        result, time = safely_exec(code, self.collection_wrapper)
        self.assertEqual(result, "Hallo\nWelt !\n")
        self.assertTrue(time < 1)

    def test_safely_exec_harmful_code(self):
        code = "print('Contents of /etc/:')\nimport os\nlist = os.listdir('/etc/')\nprint(list)"
        result, time = safely_exec(code, self.collection_wrapper)
        self.assertEqual(
            result,
            {u'error': u'The code could not be executed because it tried to do something illegal.'})
        self.assertTrue(time < 1)

    def test_safely_exec_throw_exception(self):
        code = "a = 1 / 0"
        result, time = safely_exec(code, self.collection_wrapper)
        self.assertEqual(result, {
            u'result so far': u'',
            u'error': {
                u'exception': u"<type 'exceptions.ZeroDivisionError'>",
                u'message': u'integer division or modulo by zero'
            }})
        self.assertTrue(time < 1)

    def test_safely_exec_variable_assignment(self):
        code = "string = 'Hallo Welt.'\nprint(string)"
        result, time = safely_exec(code, self.collection_wrapper)
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
print(response)
"""
        result, time = safely_exec(code, self.collection_wrapper)
        self.assertEqual(
            result,
            "[1, 1]\n")
        self.assertTrue(time < 1)

    def test_safely_exec_parsehtml_contains(self):
        code = """html = '<html><body><div style="width: 100px;">DIV</div>'
html += '<table><tr><td>A</td><td>3</td></tr></table></body></html>'
soup = factory.create('ParseHtml', html)
if soup.contains([{'tag': 'div'}]):
    print(1)
else:
    print(0)"""
        result, time = safely_exec(code, self.collection_wrapper)
        self.assertEqual(result, "1\n")
        self.assertTrue(time < 1)

    def test_safely_exec_parsehtml_find_element_and_get_attribute_value(self):
        code = """html = '<html><body><div style="width: 100px;">DIV</div>'
html += '<table><tr><td>A</td><td>3</td></tr></table></body></html>'
soup = factory.create('ParseHtml', html)
print(soup.find_element_and_get_attribute_value([{'tag': 'div'}], 'style'))"""
        result, time = safely_exec(code, self.collection_wrapper)
        self.assertEqual(result, "width: 100px;\n")
        self.assertTrue(time < 1)

    def test_safely_exec_parsehtml_find_element_and_collect_table_like_information(self):
        code = """html = '<html><body><div style="width: 100px;">DIV</div>'
html += '<table><tr><td>A</td><td>3</td></tr></table></body></html>'
soup = factory.create('ParseHtml', html)
print(soup.find_element_and_collect_table_like_information(
    [{'tag': 'table'}, {'tag': 'tr'}],
    {'a': {'search tag': 'td', 'captions': ['A'], 'content tag': 'td'}}))"""
        result, time = safely_exec(code, self.collection_wrapper)
        self.assertEqual(result, "{u'a': u'3'}\n")
        self.assertTrue(time < 1)