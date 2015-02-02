# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from socket import socketpair
from pymongo.son_manipulator import ObjectId
from multiprocessing import Process
from api_prototype.sandbox_helpers import write_exact, read_exact
from api_prototype.sandbox_helpers import write_to_pipe, read_from_pipe
from api_prototype.sandbox_helpers import escape_all_objectids_and_datetime, unescape_all_objectids_and_datetime
from api_prototype.sandbox_helpers import piped_command, NoResponseFromHostException


def host_process(pipe):
    """
    Used for testing piped_command.
    @param pipe: one end of a socketpair()
    @return:
    """
    if 'abc' in read_from_pipe(pipe):
        write_to_pipe(pipe, {'response': 123})


def errerous_host_process(pipe):
    """
    Used for testing piped_command. This should raise an exception if used with piped_command.
    @param pipe: one end of a socketpair()
    @return:
    """
    if 'abc' in read_from_pipe(pipe):
        write_to_pipe(pipe, {'notresp': 123})


class TestSandboxHelpers(TestCase):
    def test_write_exact_read_exact(self):
        pipe_in, pipe_out = socketpair()
        write_exact(pipe_in, b"abcdefg")
        self.assertEqual(read_exact(pipe_out, 7), b"abcdefg")
        write_exact(pipe_in, b"abcdefghijk")
        self.assertEqual(read_exact(pipe_out, 3), b"abc")
        self.assertEqual(read_exact(pipe_out, 8), b"defghijk")

    def test_write_to_and_read_from_pipe(self):
        pipe_in, pipe_out = socketpair()
        data = {'a': 1}
        write_to_pipe(pipe_in, data)
        self.assertEqual(read_from_pipe(pipe_out), {u'a': 1})

    def test_escape_all_objectids(self):
        id = ObjectId()
        conv_dict = {
            'a': 3,
            '_ID': id,
            'b': {'x': 3, 'y': 'blubb'}
        }
        conv_dict = escape_all_objectids_and_datetime(conv_dict)
        self.assertEqual(conv_dict['a'], conv_dict['a'])
        self.assertEqual(conv_dict['_ID'], {'ObjectId': str(id)})
        self.assertEqual(conv_dict['b'], conv_dict['b'])

    def test_unescape_all_objectids(self):
        conv_dict = {
            'a': 3,
            '_ID': {'ObjectId': '53e1d0df390b9c411387f81f'},
            'b': {'x': 3, 'y': 'blubb'}
        }
        conv_dict = unescape_all_objectids_and_datetime(conv_dict)
        self.assertEqual(conv_dict['a'], conv_dict['a'])
        self.assertIsInstance(conv_dict['_ID'], ObjectId)
        self.assertEqual(str(conv_dict['_ID']), '53e1d0df390b9c411387f81f')
        self.assertEqual(conv_dict['b'], conv_dict['b'])

    def test_piped_command(self):
        pipe_child, pipe_host = socketpair()
        host = Process(target=host_process, args=(pipe_host,))
        host.start()
        self.assertEqual(piped_command(pipe_child, {'abc': {}}), 123)
        host.join()

    def test_piped_command_error_response(self):
        pipe_child, pipe_host = socketpair()
        host = Process(target=errerous_host_process, args=(pipe_host,))
        host.start()
        with self.assertRaises(NoResponseFromHostException):
            piped_command(pipe_child, {'abc': {}})
        host.join()