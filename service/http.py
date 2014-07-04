# coding=utf-8
"""
This File is part of Pinyto
"""

from httplib import HTTPSConnection
from urllib import urlencode
from _socket import gaierror


class Https():
    """
    Objects of this class can be used to connect to remote websites.
    As such connections should always be encrypted this class only
    supports HTTPs.
    """
    def __init__(self):
        pass

    @staticmethod
    def get(domain, path):
        """
        This issues a http request to the supplied url and returns
        the response as a string. If the request fails an empty
        string is returned.

        @param domain: string
        @param path: string
        @return: string
        """
        connection = HTTPSConnection(domain)
        try:
            connection.request('GET', path)
        except gaierror:
            return ""
        response = connection.getresponse()
        if response.status != 200:
            connection.close()
            return ""
        content = response.read()
        connection.close()
        return content

    @staticmethod
    def post(domain, path="", params={}):
        """
        This issues a http request to the supplied url and returns
        the response as a string. If the request fails an empty
        string is returned.

        For the params do not forget to add an @ to the beginning of each param name.

        @param domain: string
        @param path: string
        @param params: dict
        @return: string
        """
        params = urlencode(params)
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        connection = HTTPSConnection(domain)
        try:
            connection.request('POST', path, params, headers)
        except gaierror:
            return ""
        response = connection.getresponse()
        if response.status != 200:
            connection.close()
            return ""
        content = response.read()
        connection.close()
        return content
