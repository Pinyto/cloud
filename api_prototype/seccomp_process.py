# coding=utf-8
"""
This File is part of Pinyto
"""

import json
import os
import resource
import signal
import socket
import struct

import prctl

import sys
import StringIO
import contextlib

import gc

from api_prototype.sandbox_helpers import write_exact, read_exact, _exit


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
        pid, status = os.waitpid(self.pid, os.WNOHANG)
        os.kill(self.pid, signal.SIGKILL)

    @staticmethod
    def do_exec(msg):
        """
        Execute arbitrary code sent to the child process and return the printed results
        of that code. Do not call this method from the host process because the code in
        the message gets executed with the permissions of the process!

        @param msg:
        @return: json
        """
        with stdout_io() as s:
            exec msg['body']
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

        resource.setrlimit(resource.RLIMIT_CPU, (1, 1))
        self.claim_and_free_memory()
        prctl.set_seccomp(True)
        while True:
            sz, = struct.unpack('>L', read_exact(self.child, 4))
            doc = json.loads(read_exact(self.child, sz))
            response = ''
            if doc['cmd'] == 'exec':
                response = self.do_exec(doc)
            elif doc['cmd'] == 'exit':
                _exit(0)
            json_response = json.dumps(response)
            write_exact(self.child, struct.pack('>L', len(json_response)))
            write_exact(self.child, json_response)

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

    def write_message_to_client(self, message_dict):
        """
        This constructs the json for the message and sends it to the child process.

        @param message_dict: dict
        @return: nothing
        """
        msg = json.dumps(message_dict)
        write_exact(self.host, struct.pack('>L', len(msg)))
        write_exact(self.host, msg)

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
        result = ''
        for line in code.splitlines(True):
            self.write_message_to_client({'cmd': 'exec', 'body': line})
            sz, = struct.unpack('>L', read_exact(self.host, 4))
            response = json.loads(read_exact(self.host, sz))
            if 'db.ping' in response:
                return_value = real_db.ping()
                self.write_message_to_client({'response': return_value})
            if 'result' in response:
                result += response['result']
        return result