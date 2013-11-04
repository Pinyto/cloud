import unittest
from service.database import remove_underscore_fields, remove_underscore_fields_list


class TestDatabaseHelpers(unittest.TestCase):
    def test_remove_underscore_fields(self):
        data = {'_id': 3825699854,
                'name': "Test",
                'i_count': 13}
        converted = remove_underscore_fields(data)
        self.assertEqual(converted['name'], "Test")
        self.assertEqual(converted['i_count'], 13)
        self.assertNotIn('_id', converted)

    def test_remove_underscore_fields_list(self):
        data = {'_id': 3825699854,
                'name': "Test",
                'i_count': 13}
        data_list = [data, data, data]
        converted = remove_underscore_fields_list(data_list)
        for obj in converted:
            self.assertEqual(len(obj), 2)


if __name__ == '__main__':
    unittest.main()
