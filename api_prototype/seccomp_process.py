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

import cffi
import prctl

import sys
import StringIO
import contextlib

_ffi = cffi.FFI()
_ffi.cdef('void _exit(int);')
_libc = _ffi.dlopen(None)


def _exit(n=1):
    """
    Invoke _exit(2) system call.
    """
    _libc._exit(n)


def read_exact(fp, n):
    """
    Read only the specified number of bytes

    @param fp: file pointer
    @param n: (int) number of bytes to read
    @return: byte string
    """
    buf = ''
    while len(buf) < n:
        buf2 = os.read(fp.fileno(), n)
        if not buf2:
            _exit(123)
        buf += buf2
    return buf2


def write_exact(fp, s):
    """
    Write only the specified number of bytes

    @param fp: file pointer
    @param s: (int) number of bytes to write
    @return: nothing
    """
    done = 0
    while done < len(s):
        written = os.write(fp.fileno(), s[done:])
        if not written:
            _exit(123)
        done += written


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

    def execute(self, s):
        """
        This is the host end for executing code in the child process. Code in s will be encoded as
        json and sent to the child through the open file descriptor. The host process waits till the
        result message is written to the pipe by the child process. Then the result is decoded and
        returned.

        @param s: string (which is python code and may contain multiple lines)
        @return: string
        """
        msg = json.dumps({'cmd': 'exec', 'body': s})
        write_exact(self.host, struct.pack('>L', len(msg)))
        write_exact(self.host, msg)
        sz, = struct.unpack('>L', read_exact(self.host, 4))
        response = json.loads(read_exact(self.host, sz))
        return response['result']