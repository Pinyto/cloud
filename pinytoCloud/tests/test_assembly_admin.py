# coding=utf-8
"""
This File is part of Pinyto
"""
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from pinytoCloud.models import User, StoredPublicKey, Assembly, ApiFunction, Job
from Crypto.Cipher import PKCS1_OAEP
from keyserver.settings import PINYTO_PUBLICKEY
from base64 import b16encode
import json


class TestListOwnAssemblies(TestCase):
    def setUp(self):
        self.hugo = User(name='Hugo')
        self.hugo.save()
        n = "4906219502681250223798809774327327904260276391419666181914677115202847435445452518005507304428444" + \
            "4742603016009120644035348330282759333360784030498937872562985999515117742892991032749465423946790" + \
            "9158556402591029134146090349452893554696956539933811963368734446853075386625683127394662795881747" + \
            "0894364256604860146232603404588092435482734374812471361593625543917217088490113148478038251561381" + \
            "8672330898366008493547872891602227800340728106862543870889614647176014952843513826946064902193374" + \
            "5442573561655969372352609568579364393649500357127004050087969117303304927939643892730600997930439" + \
            "1147195261326440509804663056089132784514383110912100463888066750648282272016554512713401644905102" + \
            "0092897659089644083580577942453555759938724084685541443702341305828164318826796951735041984241803" + \
            "8137353327025799036181291470746401739276004770882613670169229258999662110622086326024782780442603" + \
            "0939464832253228468472307931284129162453821959698949"
        key = StoredPublicKey.create(self.hugo, unicode(n), long(65537))
        self.session = self.hugo.start_session(key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = b16encode(pinyto_cipher.encrypt(self.session.token))

    def test_no_JSON(self):
        response = self.client.post(
            reverse('list_own_assemblies'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the token as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('list_own_assemblies'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token key.")

    def test_successful_but_empty(self):
        response = self.client.post(
            reverse('list_own_assemblies'),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertListEqual(res, [])

    def test_successful(self):
        assembly1 = Assembly(
            name='test1',
            author=self.hugo,
            description='test assembly no 1'
        )
        assembly1.save()
        func1 = ApiFunction(
            name='func1',
            code='print("Hallo Welt!")',
            assembly=assembly1
        )
        func1.save()
        func2 = ApiFunction(
            name='func2',
            code='print("Hello World!")',
            assembly=assembly1
        )
        func2.save()
        job1 = Job(
            name='job1',
            code='print("Arbeit.")',
            assembly=assembly1,
            schedule=0
        )
        job1.save()
        assembly2 = Assembly(
            name='test2',
            author=self.hugo,
            description='test assembly no 2'
        )
        assembly2.save()
        response = self.client.post(
            reverse('list_own_assemblies'),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertListEqual(res, [
            {
                u'name': u'test1',
                u'description': u'test assembly no 1',
                u'api_functions': [
                    {
                        u'name': u'func1',
                        u'code': u'print("Hallo Welt!")'
                    },
                    {
                        u'name': u'func2',
                        u'code': u'print("Hello World!")'
                    }
                ],
                u'jobs': [
                    {
                        u'name': u'job1',
                        u'code': u'print("Arbeit.")',
                        u'schedule': 0
                    }
                ]
            },
            {
                u'name': u'test2',
                u'description': u'test assembly no 2',
                u'api_functions': [],
                u'jobs': []
            }
        ])


class TestSaveAssembly(TestCase):
    def setUp(self):
        self.hugo = User(name='Hugo')
        self.hugo.save()
        n = "4906219502681250223798809774327327904260276391419666181914677115202847435445452518005507304428444" + \
            "4742603016009120644035348330282759333360784030498937872562985999515117742892991032749465423946790" + \
            "9158556402591029134146090349452893554696956539933811963368734446853075386625683127394662795881747" + \
            "0894364256604860146232603404588092435482734374812471361593625543917217088490113148478038251561381" + \
            "8672330898366008493547872891602227800340728106862543870889614647176014952843513826946064902193374" + \
            "5442573561655969372352609568579364393649500357127004050087969117303304927939643892730600997930439" + \
            "1147195261326440509804663056089132784514383110912100463888066750648282272016554512713401644905102" + \
            "0092897659089644083580577942453555759938724084685541443702341305828164318826796951735041984241803" + \
            "8137353327025799036181291470746401739276004770882613670169229258999662110622086326024782780442603" + \
            "0939464832253228468472307931284129162453821959698949"
        key = StoredPublicKey.create(self.hugo, unicode(n), long(65537))
        self.session = self.hugo.start_session(key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = b16encode(pinyto_cipher.encrypt(self.session.token))

    def test_no_JSON(self):
        response = self.client.post(
            reverse('save_assembly'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the data as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('save_assembly'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token key.")

    def test_no_original_name(self):
        response = self.client.post(
            reverse('save_assembly'),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "You have to supply an original_name and the data of the new or changed assembly.")

    def test_no_description(self):
        response = self.client.post(
            reverse('save_assembly'),
            json.dumps({
                'token': self.authentication_token,
                'original_name': 'test',
                'data': {
                    'name': 'test'
                }
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "The assembly data lacks a name or description. Both attributes must be present.")

    def test_incomplete_api_function(self):
        response = self.client.post(
            reverse('save_assembly'),
            json.dumps({
                'token': self.authentication_token,
                'original_name': 'test',
                'data': {
                    'name': 'test',
                    'description': 'This is a test.',
                    'api_functions': [
                        {
                            'name': 'func'
                        }
                    ]
                }
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "The assembly data lacks a name or code attribute in a api function.")
        self.assertListEqual(list(Assembly.objects.filter(author=self.hugo).all()), [])

    def test_incomplete_existing_api_function(self):
        test_assembly = Assembly(name='test', description='This is a test.', author=self.hugo)
        test_assembly.save()
        api_function = ApiFunction(name='func', code='blubb', assembly=test_assembly)
        api_function.save()
        response = self.client.post(
            reverse('save_assembly'),
            json.dumps({
                'token': self.authentication_token,
                'original_name': 'test',
                'data': {
                    'name': 'test',
                    'description': 'This is a test.',
                    'api_functions': [
                        {
                            'name': 'func'
                        }
                    ]
                }
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "The assembly data for changing an existing function lacks a name or code attribute.")
        self.assertListEqual(list(Assembly.objects.filter(author=self.hugo).all()), [
            test_assembly
        ])

    def test_incomplete_job(self):
        response = self.client.post(
            reverse('save_assembly'),
            json.dumps({
                'token': self.authentication_token,
                'original_name': 'test',
                'data': {
                    'name': 'test',
                    'description': 'This is a test.',
                    'jobs': [
                        {
                            'name': 'arbeito'
                        }
                    ]
                }
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "The assembly data lacks a name or code attribute in a job.")
        self.assertListEqual(list(Assembly.objects.filter(author=self.hugo).all()), [])

    def test_incomplete_existing_job(self):
        test_assembly = Assembly(name='test', description='This is a test.', author=self.hugo)
        test_assembly.save()
        job = Job(name='jobli', code='blubb', assembly=test_assembly, schedule=0)
        job.save()
        response = self.client.post(
            reverse('save_assembly'),
            json.dumps({
                'token': self.authentication_token,
                'original_name': 'test',
                'data': {
                    'name': 'test',
                    'description': 'This is a test.',
                    'jobs': [
                        {
                            'name': 'arbeito'
                        }
                    ]
                }
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(
            res['error'],
            "The assembly data for changing an existing job lacks a name or code attribute.")
        self.assertListEqual(list(Assembly.objects.filter(author=self.hugo).all()), [
            test_assembly
        ])

    def test_extend_existing_assembly(self):
        test_assembly = Assembly(name='test', description='This is a test.', author=self.hugo)
        test_assembly.save()
        api_function = ApiFunction(name='func', code='blubb', assembly=test_assembly)
        api_function.save()
        job = Job(name='jobli', code='bar', assembly=test_assembly, schedule=0)
        job.save()
        response = self.client.post(
            reverse('save_assembly'),
            json.dumps({
                'token': self.authentication_token,
                'original_name': 'test',
                'data': {
                    'name': 'test',
                    'description': 'This is a test.',
                    'api_functions': [
                        {
                            'name': 'apili',
                            'code': 'something'
                        }
                    ],
                    'jobs': [
                        {
                            'name': 'arbeito',
                            'code': 'foo'
                        },
                        {
                            'name': 'didelidi',
                            'code': 'bar'
                        }
                    ]
                }
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        for assembly in Assembly.objects.filter(author=self.hugo).all():
            self.assertEqual(assembly.api_functions.count(), 1)
            self.assertEqual(assembly.api_functions.all()[0].name, 'apili')
            self.assertEqual(assembly.api_functions.all()[0].code, 'something')
            self.assertEqual(assembly.jobs.count(), 2)
            self.assertEqual(assembly.jobs.all()[0].name, 'arbeito')
            self.assertEqual(assembly.jobs.all()[0].code, 'foo')
            self.assertEqual(assembly.jobs.all()[1].name, 'didelidi')
            self.assertEqual(assembly.jobs.all()[1].code, 'bar')

    def test_new_assembly(self):
        response = self.client.post(
            reverse('save_assembly'),
            json.dumps({
                'token': self.authentication_token,
                'original_name': 'test',
                'data': {
                    'name': 'test',
                    'description': 'This is a test.',
                    'api_functions': [
                        {
                            'name': 'apili',
                            'code': 'something'
                        }
                    ],
                    'jobs': [
                        {
                            'name': 'arbeito',
                            'code': 'foo'
                        },
                        {
                            'name': 'didelidi',
                            'code': 'bar'
                        }
                    ]
                }
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        for assembly in Assembly.objects.filter(author=self.hugo).all():
            self.assertEqual(assembly.api_functions.count(), 1)
            self.assertEqual(assembly.api_functions.all()[0].name, 'apili')
            self.assertEqual(assembly.api_functions.all()[0].code, 'something')
            self.assertEqual(assembly.jobs.count(), 2)
            self.assertEqual(assembly.jobs.all()[0].name, 'arbeito')
            self.assertEqual(assembly.jobs.all()[0].code, 'foo')
            self.assertEqual(assembly.jobs.all()[1].name, 'didelidi')
            self.assertEqual(assembly.jobs.all()[1].code, 'bar')

    def test_rename_assembly(self):
        test_assembly = Assembly(name='test1', description='This is a test.', author=self.hugo)
        test_assembly.save()
        api_function = ApiFunction(name='func', code='blubb', assembly=test_assembly)
        api_function.save()
        job = Job(name='jobli', code='bar', assembly=test_assembly, schedule=0)
        job.save()
        response = self.client.post(
            reverse('save_assembly'),
            json.dumps({
                'token': self.authentication_token,
                'original_name': 'test1',
                'data': {
                    'name': 'test2',
                    'description': 'This is a test.',
                    'api_functions': [
                        {
                            'name': 'func',
                            'code': 'something'
                        }
                    ],
                    'jobs': [
                        {
                            'name': 'arbeito',
                            'code': 'foo',
                            'schedule': 12
                        },
                        {
                            'name': 'jobli',
                            'code': 'dudeldei'
                        }
                    ]
                }
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        for assembly in Assembly.objects.filter(author=self.hugo).all():
            self.assertEqual(assembly.name, 'test2')
            self.assertEqual(assembly.api_functions.count(), 1)
            self.assertEqual(assembly.api_functions.all()[0].name, 'func')
            self.assertEqual(assembly.api_functions.all()[0].code, 'something')
            self.assertEqual(assembly.jobs.count(), 2)
            self.assertEqual(assembly.jobs.all()[0].name, 'jobli')
            self.assertEqual(assembly.jobs.all()[0].code, 'dudeldei')
            self.assertEqual(assembly.jobs.all()[1].name, 'arbeito')
            self.assertEqual(assembly.jobs.all()[1].code, 'foo')


class TestDeleteAssembly(TestCase):
    def setUp(self):
        self.hugo = User(name='Hugo')
        self.hugo.save()
        n = "4906219502681250223798809774327327904260276391419666181914677115202847435445452518005507304428444" + \
            "4742603016009120644035348330282759333360784030498937872562985999515117742892991032749465423946790" + \
            "9158556402591029134146090349452893554696956539933811963368734446853075386625683127394662795881747" + \
            "0894364256604860146232603404588092435482734374812471361593625543917217088490113148478038251561381" + \
            "8672330898366008493547872891602227800340728106862543870889614647176014952843513826946064902193374" + \
            "5442573561655969372352609568579364393649500357127004050087969117303304927939643892730600997930439" + \
            "1147195261326440509804663056089132784514383110912100463888066750648282272016554512713401644905102" + \
            "0092897659089644083580577942453555759938724084685541443702341305828164318826796951735041984241803" + \
            "8137353327025799036181291470746401739276004770882613670169229258999662110622086326024782780442603" + \
            "0939464832253228468472307931284129162453821959698949"
        key = StoredPublicKey.create(self.hugo, unicode(n), long(65537))
        self.session = self.hugo.start_session(key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = b16encode(pinyto_cipher.encrypt(self.session.token))

    def test_no_JSON(self):
        response = self.client.post(
            reverse('delete_assembly'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the data as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('delete_assembly'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token key.")

    def test_no_name(self):
        response = self.client.post(
            reverse('delete_assembly'),
            json.dumps({
                'token': self.authentication_token
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "You have to supply the name of the assembly you want to delete.")

    def test_wrong_name(self):
        doomed_assembly = Assembly(name='doomed_assembly', description='dudeldi', author=self.hugo)
        doomed_assembly.save()
        response = self.client.post(
            reverse('delete_assembly'),
            json.dumps({
                'token': self.authentication_token,
                'name': 'foo'
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "There was no assembly found with the name foo.")

    def test_successful(self):
        doomed_assembly = Assembly(name='doomed_assembly', description='dudeldi', author=self.hugo)
        doomed_assembly.save()
        response = self.client.post(
            reverse('delete_assembly'),
            json.dumps({
                'token': self.authentication_token,
                'name': 'doomed_assembly'
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertEqual(Assembly.objects.filter(author=self.hugo).count(), 0)


class TestListInstalledAssemblies(TestCase):
    def setUp(self):
        self.hugo = User(name='Hugo')
        self.hugo.save()
        n = "4906219502681250223798809774327327904260276391419666181914677115202847435445452518005507304428444" + \
            "4742603016009120644035348330282759333360784030498937872562985999515117742892991032749465423946790" + \
            "9158556402591029134146090349452893554696956539933811963368734446853075386625683127394662795881747" + \
            "0894364256604860146232603404588092435482734374812471361593625543917217088490113148478038251561381" + \
            "8672330898366008493547872891602227800340728106862543870889614647176014952843513826946064902193374" + \
            "5442573561655969372352609568579364393649500357127004050087969117303304927939643892730600997930439" + \
            "1147195261326440509804663056089132784514383110912100463888066750648282272016554512713401644905102" + \
            "0092897659089644083580577942453555759938724084685541443702341305828164318826796951735041984241803" + \
            "8137353327025799036181291470746401739276004770882613670169229258999662110622086326024782780442603" + \
            "0939464832253228468472307931284129162453821959698949"
        key = StoredPublicKey.create(self.hugo, unicode(n), long(65537))
        self.session = self.hugo.start_session(key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = b16encode(pinyto_cipher.encrypt(self.session.token))

    def test_no_JSON(self):
        response = self.client.post(
            reverse('list_installed_assemblies'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the data as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('list_installed_assemblies'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token key.")

    def test_empty_list(self):
        response = self.client.post(
            reverse('list_installed_assemblies'),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertListEqual(res, [])

    def test_successful(self):
        test_assembly = Assembly(name='test1', description='This is a test.', author=self.hugo)
        test_assembly.save()
        api_function = ApiFunction(name='func', code='blubb', assembly=test_assembly)
        api_function.save()
        job = Job(name='jobli', code='bar', assembly=test_assembly, schedule=0)
        job.save()
        self.hugo.installed_assemblies.add(test_assembly)
        self.hugo.save()
        response = self.client.post(
            reverse('list_installed_assemblies'),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertListEqual(res, [{
            u'author': u'Hugo',
            u'description': u'This is a test.',
            u'name': u'test1'
        }])


class TestListAllAssemblies(TestCase):
    def setUp(self):
        self.hugo = User(name='Hugo')
        self.hugo.save()
        n = "4906219502681250223798809774327327904260276391419666181914677115202847435445452518005507304428444" + \
            "4742603016009120644035348330282759333360784030498937872562985999515117742892991032749465423946790" + \
            "9158556402591029134146090349452893554696956539933811963368734446853075386625683127394662795881747" + \
            "0894364256604860146232603404588092435482734374812471361593625543917217088490113148478038251561381" + \
            "8672330898366008493547872891602227800340728106862543870889614647176014952843513826946064902193374" + \
            "5442573561655969372352609568579364393649500357127004050087969117303304927939643892730600997930439" + \
            "1147195261326440509804663056089132784514383110912100463888066750648282272016554512713401644905102" + \
            "0092897659089644083580577942453555759938724084685541443702341305828164318826796951735041984241803" + \
            "8137353327025799036181291470746401739276004770882613670169229258999662110622086326024782780442603" + \
            "0939464832253228468472307931284129162453821959698949"
        key = StoredPublicKey.create(self.hugo, unicode(n), long(65537))
        self.session = self.hugo.start_session(key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = b16encode(pinyto_cipher.encrypt(self.session.token))

    def test_no_JSON(self):
        response = self.client.post(
            reverse('list_all_assemblies'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the data as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('list_all_assemblies'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token key.")

    def test_successful(self):
        test_assembly = Assembly(name='test1', description='This is a test.', author=self.hugo)
        test_assembly.save()
        api_function = ApiFunction(name='func', code='blubb', assembly=test_assembly)
        api_function.save()
        job = Job(name='jobli', code='bar', assembly=test_assembly, schedule=0)
        job.save()
        response = self.client.post(
            reverse('list_all_assemblies'),
            json.dumps({'token': self.authentication_token}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertGreaterEqual(len(res), 1)
        found = False
        for assembly in res:
            if assembly['name'] == u'test1':
                self.assertEqual(assembly, {
                    u'author': u'Hugo',
                    u'description': u'This is a test.',
                    u'name': u'test1'
                })
                found = True
        self.assertTrue(found)


class TestInstallAssembly(TestCase):
    def setUp(self):
        self.hugo = User(name='Hugo')
        self.hugo.save()
        n = "4906219502681250223798809774327327904260276391419666181914677115202847435445452518005507304428444" + \
            "4742603016009120644035348330282759333360784030498937872562985999515117742892991032749465423946790" + \
            "9158556402591029134146090349452893554696956539933811963368734446853075386625683127394662795881747" + \
            "0894364256604860146232603404588092435482734374812471361593625543917217088490113148478038251561381" + \
            "8672330898366008493547872891602227800340728106862543870889614647176014952843513826946064902193374" + \
            "5442573561655969372352609568579364393649500357127004050087969117303304927939643892730600997930439" + \
            "1147195261326440509804663056089132784514383110912100463888066750648282272016554512713401644905102" + \
            "0092897659089644083580577942453555759938724084685541443702341305828164318826796951735041984241803" + \
            "8137353327025799036181291470746401739276004770882613670169229258999662110622086326024782780442603" + \
            "0939464832253228468472307931284129162453821959698949"
        key = StoredPublicKey.create(self.hugo, unicode(n), long(65537))
        self.session = self.hugo.start_session(key)
        self.hugo.last_calculation_time = timezone.now()
        self.hugo.save()
        pinyto_cipher = PKCS1_OAEP.new(PINYTO_PUBLICKEY)
        self.authentication_token = b16encode(pinyto_cipher.encrypt(self.session.token))

    def test_no_JSON(self):
        response = self.client.post(
            reverse('install_assembly'),
            "Didelidi",
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply the data as JSON.")

    def test_no_token(self):
        response = self.client.post(
            reverse('install_assembly'),
            json.dumps({'x': 1234}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "Please supply JSON with a token key.")

    def test_no_user(self):
        response = self.client.post(
            reverse('install_assembly'),
            json.dumps({
                'token': self.authentication_token
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "You have to supply an author to install an assembly.")

    def test_wrong_user(self):
        response = self.client.post(
            reverse('install_assembly'),
            json.dumps({
                'token': self.authentication_token,
                'author': 'Bilbo'
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "There was no user found with the name Bilbo.")

    def test_no_assembly(self):
        response = self.client.post(
            reverse('install_assembly'),
            json.dumps({
                'token': self.authentication_token,
                'author': 'Hugo'
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "You have to supply the name of the assembly you want to install.")

    def test_wrong_assembly(self):
        response = self.client.post(
            reverse('install_assembly'),
            json.dumps({
                'token': self.authentication_token,
                'author': 'Hugo',
                'name': 'Foo'
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertIn('error', res)
        self.assertEqual(res['error'], "There was no assembly found with the name Hugo/Foo.")

    def test_successful(self):
        foo = Assembly(name='Foo', description='Bar', author=self.hugo)
        foo.save()
        response = self.client.post(
            reverse('install_assembly'),
            json.dumps({
                'token': self.authentication_token,
                'author': 'Hugo',
                'name': 'Foo'
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertNotIn('error', res)
        self.assertIn('success', res)
        self.assertTrue(res['success'])
        self.assertEqual(self.hugo.installed_assemblies.count(), 1)
        self.assertEqual(self.hugo.installed_assemblies.all()[0].name, 'Foo')