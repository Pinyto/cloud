# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from socket import socketpair
from multiprocessing import Process
from api_prototype.sandbox_helpers import write_exact, read_exact
from api_prototype.sandbox_helpers import write_to_pipe, read_from_pipe
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
        write_exact(pipe_in, "abcdefg")
        self.assertEqual(read_exact(pipe_out, 7), "abcdefg")
        write_exact(pipe_in, "abcdefghijk")
        self.assertEqual(read_exact(pipe_out, 3), "abc")
        self.assertEqual(read_exact(pipe_out, 8), "defghijk")

    def test_write_to_and_read_from_pipe(self):
        pipe_in, pipe_out = socketpair()
        data = {'a': 1}
        write_to_pipe(pipe_in, data)
        self.assertEqual(read_from_pipe(pipe_out), {u'a': 1})

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