# coding=utf-8
"""
This File is part of Pinyto
"""

import os
import resource
import signal
import socket

import prctl

import sys
import StringIO
import contextlib

import gc
import json

from api_prototype.sandbox_helpers import libc_exit, write_to_pipe, read_from_pipe
from api_prototype.models import SandboxCollectionWrapper


@contextlib.contextmanager
def stdout_io(stdout=None):
    """
    Sets stdout.

    @param stdout:
    @return:
    """
    old = sys.stdout
    if stdout is None:
        stdout = StringIO.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


class SecureHost(object):
    """
    Create an instance of this class to fork this process and secure the child with seccomp.
    This can be used to exec possibly insecure code without risking data loss or system
    instability.
    """
    def __init__(self):
        self.host, self.child = socket.socketpair()
        self.pid = None

    def start_child(self):
        """
        This starts the child process and executes the _child_main on the child process.
        The socket used for communication gets closed afterwards.

        @return: nothing
        """
        assert not self.pid
        self.pid = os.fork()
        if not self.pid:
            self._child_main()
        self.child.close()

    def kill_child(self):
        """
        This kills the child process.

        @return: nothing
        """
        assert self.pid
        os.waitpid(self.pid, os.WNOHANG)
        try:
            os.kill(self.pid, signal.SIGKILL)
        except OSError:
            pass

    @staticmethod
    def do_exec(msg, db):
        """
        Execute arbitrary code sent to the child process and return the printed results
        of that code. Do not call this method from the host process because the code in
        the message gets executed with the permissions of the process!

        @param msg:
        @return: json
        """
        with stdout_io() as s:
            try:
                exec msg['body']
            except Exception as e:
                return {'exception': str(type(e)), 'message': str(e)}
        return {'result': s.getvalue()}

    def _child_main(self):
        """
        This method must only be called by the child process (see start_child()) so it is better
        to close the host side of the communication. After that we try to close all accessible
        file descriptors which are not needed (we only need self.child). If closing of these fails
        (OSError) then that is no issue because the child process will not be able to do anything
        harmful with them. After that we limit the child process to a maximum of one second CPU
        time.
        Then we activate seccomp. After that the child process will not be able to allocate big
        amounts of memory, import anything or do anything else which includes system calls other
        than reading from or writing to existing file descriptors.
        In the while loop we read commands passed to the child as json and exec the code from the
        message or exit. After each command the results are written to the file descriptor as
        json.

        @return: nothing; the output is written to self.child
        """
        self.host.close()
        for fd in map(int, os.listdir('/proc/self/fd')):
            if fd != self.child.fileno():
                try:
                    os.close(fd)
                except OSError:
                    pass

        db = SandboxCollectionWrapper(self.child)
        self.claim_and_free_memory()
        resource.setrlimit(resource.RLIMIT_CPU, (1, 1))
        prctl.set_seccomp(True)
        while True:
            doc = read_from_pipe(self.child)
            response = ''
            if doc['cmd'] == 'exec':
                response = self.do_exec(doc, db)
            elif doc['cmd'] == 'exit':
                libc_exit(0)
            write_to_pipe(self.child, response)

    def claim_memory(self, iteration=0):
        """
        This claims some memory to insure the heap is big enough for most api scripts.

        @param iteration: integer
        @return: nothing
        """
        useless_list = []
        for i in range(100):
            useless_list.append(range(100))
        if iteration < 100:
            self.claim_memory(iteration + 1)

    def claim_and_free_memory(self):
        """
        This function uses claim_memory to claim memory on the heap and starts the garbage
        collector to free this memory.

        @return: nothing
        """
        self.claim_memory()
        gc.collect()

    def execute(self, code, real_db):
        """
        This is the host end for executing code in the child process. Code in s will be encoded as
        json and sent to the child through the open file descriptor. The host process waits till the
        result message is written to the pipe by the child process. Then the result is decoded and
        returned.

        @param code: string (which is python code and may contain multiple lines)
        @param real_db: CollectionWrapper
        @return: string
        """
        result = u''
        write_to_pipe(self.host, {'cmd': 'exec', 'body': code})
        result_received = False
        while not result_received:
            response = read_from_pipe(self.host)
            if 'exception' in response:
                return {u'error': response, u'result so far': result}
            elif 'db.find' in response:
                return_value = real_db.find(
                    response['db.find']['query'],
                    response['db.find']['limit'])
                write_to_pipe(self.host, {'response': return_value})
            elif 'db.count' in response:
                return_value = real_db.count(response['db.count']['query'])
                write_to_pipe(self.host, {'response': str(return_value)})
            elif 'db.find_documents' in response:
                return_value = real_db.find_documents(
                    response['db.find_documents']['query'],
                    response['db.find_documents']['limit'])
                write_to_pipe(self.host, {'response': return_value})
            elif 'db.find_document_for_id' in response:
                return_value = real_db.find_document_for_id(
                    response['db.find_document_for_id']['document_id'])
                write_to_pipe(self.host, {'response': return_value})
            elif 'db.save' in response:
                real_db.save(response['db.save']['document'])
                write_to_pipe(self.host, {'response': True})
            elif 'db.insert' in response:
                real_db.insert(response['db.insert']['document'])
                write_to_pipe(self.host, {'response': True})
            elif 'db.remove' in response:
                real_db.remove(response['db.remove']['document'])
                write_to_pipe(self.host, {'response': True})
            elif 'result' in response:
                result_received = True
                result += response['result']
            else:
                write_to_pipe(self.host, {'error': "No command and no result."})
        return result