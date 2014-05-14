# coding=utf-8
"""
This File is part of Pinyto
"""

import random


def create_token(length=16):
    """
    Creates a hexadecimal token string (0-9,a-f) of length length.

    @param length: int
    @return: string
    """
    ru = lambda: hex(random.randint(0, 15))[2]
    return ''.join([ru() for _ in xrange(length)])