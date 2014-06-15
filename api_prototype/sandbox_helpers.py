# coding=utf-8
"""
This File is part of Pinyto
"""

import cffi
import os


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
    return buf  # TODO: originally buf2 was returned but that prpably maken no sense.


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