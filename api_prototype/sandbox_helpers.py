# coding=utf-8
"""
This File is part of Pinyto
"""

import cffi
import os
import json
import struct
from pymongo.son_manipulator import ObjectId


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
    @param s: string to write and not a byte more than that
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


def escape_all_objectids_and_datetime(conv_dict):
    """
    This function escapes all ObjectId objects to make the dict json serializable.

    @param conv_dict:
    @return:
    """
    for key in conv_dict.keys():
        if type(conv_dict[key]) == dict:
            conv_dict[key] = escape_all_objectids_and_datetime(conv_dict[key])
        elif type(conv_dict[key]) == ObjectId:
            conv_dict[key] = {'ObjectId': str(conv_dict[key])}
    return conv_dict


def unescape_all_objectids_and_datetime(conv_dict):
    """
    This function reverses the escape of all ObjectId objects done by escape_all_objectids_and_datetime.

    @param conv_dict:
    @return:
    """
    for key in conv_dict.keys():
        if type(conv_dict[key]) == dict:
            if 'ObjectId' in conv_dict[key]:
                conv_dict[key] = ObjectId(conv_dict[key]['ObjectId'])
            else:
                conv_dict[key] = unescape_all_objectids_and_datetime(conv_dict[key])
    return conv_dict


def piped_command(pipe, command_dict):
    """
    Writes the command_dict to the pipe end reads the answer.

    @param pipe: one part of socket.socketpair()
    @param command_dict: dict
    @return:
    """
    write_to_pipe(pipe, command_dict)
    answer = read_from_pipe(pipe)
    if 'response' in answer:
        return answer['response']
    else:
        raise NoResponseFromHostException(
            str(command_dict) + ' returned no valid response. ' +
            'This means the host process lacks an implementation for this command.')


class NoResponseFromHostException(Exception):
    """
    This is a custom exception which gets returned if no valid response is returned.
    """