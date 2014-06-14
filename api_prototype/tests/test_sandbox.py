# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from pinytoCloud.models import User
from api_prototype.sandbox import safely_exec


class TestSandbox(TestCase):
    def test_safely_exec(self):
        code = "print('Hallo')\nprint('Welt !')"
        hugo = User(name='hugo')
        hugo.save()
        result, time = safely_exec(code, hugo)
        self.assertEqual(result, "Hallo\nWelt !\n")
        self.assertTrue(time < 1)

    def test_safely_exec_harmful_code(self):
        code = "print('Contents of /etc/:')\nimport os\nlist = os.listdir('/etc/')\nprint(list)"
        hugo = User(name='hugo')
        hugo.save()
        result, time = safely_exec(code, hugo)
        self.assertEqual(
            result,
            {'error': 'The code could not be executed because it tried to do something illegal.'})
        self.assertTrue(time < 1)