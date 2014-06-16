# coding=utf-8
"""
This File is part of Pinyto
"""

import cffi
import os
import json
import struct


_ffi = cffi.FFI()
_ffi.cdef('void _exit(int);')
_libc = _ffi.dlopen(None)


def libc_exit(n=1):
    """
    Invoke _exit(2) system call.

    @param n: int
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
            libc_exit(123)
        buf += buf2
    return buf  # TODO: originally buf2 was returned but that prpably makes no sense.


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
            libc_exit(123)
        done += written


def write_to_pipe(pipe, data_dict):
    """
    Writes the data_dict to the give pipe.

    @param pipe: one part of socket.socketpair()
    @param data_dict: dict
    @return: nothing
    """
    data_json = json.dumps(data_dict)
    write_exact(pipe, struct.pack('>L', len(data_json)))
    write_exact(pipe, data_json)


def read_from_pipe(pipe):
    """
    Reads a json string from the pipe and decodes the json of that string.

    @param pipe: one part of socket.socketpair()
    @return: dict
    """
    sz, = struct.unpack('>L', read_exact(pipe, 4))
    return json.loads(read_exact(pipe, sz))