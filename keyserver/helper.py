# coding=utf-8
"""
This File is part of Pinyto
"""

from http.client import HTTPSConnection
from urllib.parse import urlencode
import random


def secure_request(domain, path, request_type='GET', params=None):
    """
    This issues a http request to the supplied url ant returns
    the response as a string. If the request fails an empty
    string is returned.

    @param domain: string
    @param path: string
    @param request_type: 'GET' or 'POST'
    @param params: dict
    @return: string
    """
    if not params:
        params = {}
    params = urlencode(params)
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    connection = HTTPSConnection(domain)
    connection.request(request_type, path, params, headers)
    response = connection.getresponse()
    if response.status != 200:
        connection.close()
        return "" + response.status
    content = response.read()
    connection.close()
    return content


def create_salt(length=10):
    """
    Creates a unicode string of the given length.

    @param length: integer
    @return: string
    """
    ru = lambda: chr(random.randint(33, 127))
    return ''.join([ru() for _ in range(length)])
